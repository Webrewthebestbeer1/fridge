from flask_restful import Resource, Api, reqparse
import json

from agent import Agent
from app import app, db, Reading, Sensor, FridgeEncoder

api = Api(app)
parser = reqparse.RequestParser()
agent = Agent(2)

class GetSensorReadings(Resource):
    def get(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('limit', type=int, help='Limit')
            args = parser.parse_args()
            limit = args['limit']
            if not limit:
                readings = Reading.query.all()
            else:
                readings = Reading.query.order_by(Reading.date.desc()).limit(limit).all()
            if not readings: return {'readings': {}}
            return {'readings': json.dumps(readings, cls=FridgeEncoder)}
        except Exception as e:
            return {'error': str(e)}


class GetTargetTemp(Resource):
    def get(self):
        agent.read_sensors()
        return {'target_temp': agent.get_target_temp()}

class SetTargetTemp(Resource):
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('target_temp', type=int, help='Target temperature')
            args = parser.parse_args()
            _target_temp = args['target_temp']
            if not _target_temp: raise Exception('no valid arguments')
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
        use_reloader=False # initiates APScheduler twice if True
    )
