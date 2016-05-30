from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from json import JSONEncoder
import datetime


app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
  return response

class Reading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.datetime.now)
    target_temp = db.Column(db.Integer)
    compressor_state = db.Column(db.Boolean)
    sensors = db.relationship('Sensor')

    def serialize(self):
        return {
            'date': self.date.isoformat(),
            'target_temp': self.target_temp,
            'compressor_state': self.compressor_state,
            'sensors': {sensor.placement: sensor.value for sensor in self.sensors}
        }

class Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float)
    placement = db.Column(db.String)
    reading_id = db.Column(db.Integer, db.ForeignKey('reading.id'))

class FridgeEncoder(JSONEncoder):
    def default(self, o):
        return o.get_dict()
