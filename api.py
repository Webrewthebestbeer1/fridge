from flask_restful import Resource, Api, reqparse
from flask import jsonify
from datetime import datetime

from agent import Agent
from app import app, db, Reading, Sensor
from app import app as application

api = Api(app)
parser = reqparse.RequestParser()
latest_reading = Reading.query.order_by(Reading.date.desc()).first()
if not latest_reading:
    agent = Agent(19)
else:
    agent = Agent(latest_reading.target_temp)


class GetSensorReadings(Resource):
    def get(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('limit', type=int, help='Limit')
            parser.add_argument('from', type=str, help='From')
            parser.add_argument('to', type=str, help='To')
            args = parser.parse_args()
            limit = args['limit']
            from_date = args['from']
            to_date = args['to']
            if from_date and to_date:
                date_format = '%Y-%m-%dT%H:%M'
                from_date = datetime.strptime(from_date, date_format)
                to_date = datetime.strptime(to_date, date_format)
                if not from_date.date() == to_date.date():
                    raise Exception('Range must be on same day')
                print(from_date, to_date)
                """
                As the graph should not load more than around 50 entries
                we select only the n-th elements from the table
                """
                entries = (to_date - from_date).seconds / 60
                n = int(entries / 50)
                results = db.engine.execute(
                    "SELECT * FROM reading WHERE \
                    (date >= '" + str(from_date) + "' AND \
                    date <= '" + str(to_date) + "') AND \
                    (rowid - (SELECT rowid FROM reading WHERE \
                    date > '" + str(from_date) + "' ORDER BY date LIMIT 1)) \
                    % " + str(n) + " = 0;"
                )
                readings = [Reading.query.get(result.id) for result in results]
                return jsonify([reading.serialize() for reading in readings])
            if not limit:
                limit = 20
            readings = Reading.query.order_by(
                Reading.date.desc()
            ).limit(limit).all()
            readings.reverse()
            return jsonify([reading.serialize() for reading in readings])
        except Exception as e:
            return {'error': str(e)}


class GetTargetTemp(Resource):
    def get(self):
        return {'target_temp': agent.get_target_temp()}


class SetTargetTemp(Resource):
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument(
                'target_temp',
                type=int,
                help='Target temperature'
            )
            args = parser.parse_args()
            _target_temp = args['target_temp']
            if not _target_temp:
                raise Exception('no valid arguments')
            agent.set_target_temp(_target_temp)
            return {'target_temp': _target_temp}
        except Exception as e:
            return {'error': str(e)}


api.add_resource(GetSensorReadings, '/get_sensor_readings')
api.add_resource(GetTargetTemp, '/get_target_temp')
api.add_resource(SetTargetTemp, '/set_target_temp')


if __name__ == '__main__':
    app.run(
        debug=app.config['DEBUG'],
    )
