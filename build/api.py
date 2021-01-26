from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
import pymysql
import sys
sys.path.insert(1, '/Users/josh/Desktop/Capstone')
import secrets

app = Flask(__name__)
api = Api(app)
engine = "mysql+pymysql://{0}:{1}@{2}/{3}".format(secrets.user, secrets.password, secrets.host, secrets.name)
app.config['SQLALCHEMY_DATABASE_URI'] = engine
db = SQLAlchemy(app)
@app.route("/")


#Table creation
#Device Table
class DeviceModel(db.Model):
    __tablename__ = 'devices'
    name = db.Column(db.String(20), nullable = False, unique = True)
    IDdevice = db.Column(db.Integer, primary_key = True)
    device_type = db.Column(db.String(20), nullable = False)
    device_ip = db.Column(db.String(15), nullable = False)
    device_edgeID = db.Column(db.Integer, db.ForeignKey('edgestations.edgeID'), nullable = False)
    #edgeID = db.relationship('EdgeStationsModel', backref = db.backref('posts', lazy = True))


    def __repr__(self):
        return f"Devices(name ={name}, device ID = {IDdevice}, device type = {device_type}, '{self.device_edgeID}') " 

#Edge Stations Table
class EdgeStationsModel(db.Model):
    __tablename__ = 'edgestations'
    edgeID = db.Column(db.Integer, primary_key = True)
    edge_name = db.Column(db.String(20), nullable = False, unique = True)
    edge_ip = db.Column(db.String(15), nullable = False)
    edge_port = db.Column(db.Integer, nullable = False)

    def __repr__(self):
        return f"EdgeStation('{self.edgeID}', '{self.edge_name}', '{self.edge_ip}'')"
 
#Readings Table
'''
class ReadingsModel(db.Model):
    __tablename__ = 'readings'
    applicationID = db.Column(db.Integer, primary_key = True)
'''

'''  
class EventsModel(db.Model):
    __tablename__ = 'events'
    applicationID = db.Column(db.Integer, primary_key = True)

class PredictionsModel(db.Model):
    __tablename__ = 'predictions'
    applicationID = db.Column(db.Integer, primary_key = True)
'''

#device request parsers
devices_put_args = reqparse.RequestParser()
devices_put_args.add_argument("name", type=str, help="Name of device is required", required=True)
devices_put_args.add_argument("device_type", type=str, help="Type of device is required", required=True)
devices_put_args.add_argument("deviceID", type=int, help="ID of device is required", required=True)

device_update_args = reqparse.RequestParser()
device_update_args.add_argument("name", type=str, help="Name of device is required")
device_update_args.add_argument("device_type", type=str, help="Type of device is required")

device_fields = {
    'IDdevice' : fields.Integer,
    'name' : fields.String,
    'device_type': fields.String,
    'device_edgeID' : fields.Integer
}


#edge station request parsers
edge_put_args = reqparse.RequestParser()
edge_put_args.add_argument("edge_name", type=str, help="Name of edge is required", required=True)
edge_put_args.add_argument("edge_ip", type=str, help="Edge IP is required", required=True)
edge_put_args.add_argument("edegeID", type=int, help="ID of device is required", required=True)

edge_update_args = reqparse.RequestParser()
edge_update_args.add_argument("edge_name", type=str, help="Name of edege is required")
edge_update_args.add_argument("device_ip", type=str, help="IP of device is required")


edgestation_fields = {
    'edgeID' : fields.Integer,
    'edge_name' : fields.String,
    'edge_ip' : fields.String,
    'edge_port' : fields.Integer
}



#Classes for each component
class Devices(Resource):
    @marshal_with(device_fields)
    def get(self, device_id):
        result = DeviceModel.query.filter_by(IDdevice = device_id).first()
        if not result:
            abort(404, message = "Could not find device")
        return result
        
    @marshal_with(device_fields)
    def put(self, device_id):
        args = devices_put_args.parse_args()
        result = DeviceModel.query.filter_by(IDdevice = device_id).first()
        if result:
            abort(409, message = "Device ID exists")
        device = DeviceModel(name = args['name'], IDdevice = device_id, device_type = args['device_type'])
        db.session.add(device)
        db.session.commit()
        return device, 201
    
    @marshal_with(device_fields) 
    def patch(self, device_id):
        args = device_update_args.parse_args()
        result = DeviceModel.query.filter_by(IDdevice = device_id).first()
        if not result:
            abort(404, message = "No such device, update failed") 
        if args['name']:
            result.name = args['name']
        if args['device_type']:
            result.device_type = args['device_type']

        db.session.commit()

        return result

class EdgeStation(Resource):
    @marshal_with(edgestation_fields)
    def get(self, edgestation_id):
        result = EdgeStationsModel.query.filter_by(edgeID = edgestation_id).first()
        if not result:
            abort(404, message = "No such edge station")
        return result
    
    @marshal_with(edgestation_fields)
    def put(self, edgestation_id):
        args = edge_put_args.parse_args()
        result = EdgeStationsModel.query.filter_by(edgeID = edgestation_id).first()
        if result:
            abort(409, message = "Edgestation already exists")
        edgestation = DeviceModel(edge_name = args['edge_name'], edgeID = edgestation_id, edge_ip = args['edge_ip'])
        db.session.add(edgestation)
        db.session.commit()
        return edgestation, 201

api.add_resource(Devices, '/devices/<int:device_id>')
api.add_resource(EdgeStation, '/edgestation/<int:edgestation_id>')



class ReturnDevices(Resource):
    @marshal_with(device_fields)
    def get(self):
        result = DeviceModel.query.all()
        return result

class ReturnEdgeStations(Resource):
    @marshal_with(edgestation_fields)
    def get(self):
        result = EdgeStationsModel.query.all()
        return result


api.add_resource(ReturnEdgeStations, '/edgestations')
api.add_resource(ReturnDevices, '/devices')

if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = 8080, debug = True)

