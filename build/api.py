from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/database.db'
db = SQLAlchemy(app)


class DeviceModel(db.Model):
    __tablename__ = 'devices'
    deviceID = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20), nullable = False)
    device_type = db.Column(db.Integer, nullable = False)
    edgeID = db.Column(db.Integer, db.ForeignKey('edgestations.edgeID'), nullable = False)
    edgestations = db.relationship('EdgeStationsModel', backref = db.backref('posts', lazy = True))


    def __repr__(self):
        return f"Devices(name ={name}, deviceID = {deviceID}, device_type = {device_type}) " 

class EdgeStationsModel(db.Model):
    __tablename__ = 'edge_stations'
    edgeID = db.Column(db.Integer, primary_key = True)
    edge_name = db.Column(db.String(20), nullable = False)
    edge_ip = db.Column(db.String(15), nullable = False)
    edge_port = db.Column(db.Integer, nullable = False)
'''
class ReadingsModel(db.Model):
    __tablename__ = 'readings'
    applicationID = db.Column(db.Integer, primary_key = True)
    
class EventsModel(db.Model):
    __tablename__ = 'events'
    applicationID = db.Column(db.Integer, primary_key = True)

class PredictionsModel(db.Model):
    __tablename__ = 'predictions'
    applicationID = db.Column(db.Integer, primary_key = True)
'''

db.create_all()

devices_put_args = reqparse.RequestParser()
devices_put_args.add_argument("name", type=str, help="Name of device is required", required=True)
devices_put_args.add_argument("device_type", type=str, help="Type of device is required", required=True)
devices_put_args.add_argument("deviceID", type=int, help="ID of device is required", required=True)



device_fields = {
    'deviceID' : fields.Integer,
    'name' : fields.String,
    'device_type': fields.String,
    'edgeID': fields.Integer
}

class Devices():
    @marshal_with(device_fields)
    def get(self, device_id):
        result = DeviceModel.query.get(deviceID = device_id)
        return result
        
    @marshal_with(device_fields)
    def put(self, device_id):
        args = devices_put_args.parse_args()
        device = DeviceModel(deviceID = device_id, name = args['name'], device_type = args['device_type'], edgeID = args['edgeID'])
        db.session.add(device)
        db.session.commit()
        return device, 201
'''
class EdgeStation():
    def get(self, edgestation_id):
        result = EdgeStationsModel.query.get(edgestation_id = edgestation_id)
'''


if __name__ == "__main__":
    app.run(debug = True)

