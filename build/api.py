from flask import Flask, render_template
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
def HomePage():
    return render_template("home.html")



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
 
#Events Table
class EventsModel(db.Model):
    __tablename__ = 'event'
    idee = db.Column(db.Integer, primary_key = True)
    event_id = db.Column(db.Integer, nullable = True, unique = True)
    event_name = db.Column(db.String(30), nullable = True, unique = True)
    event_condition_type = db.Column(db.String(50))
    event_condition = db.Column(db.Float)
    IDdevice = db.Column(db.Integer, db.ForeignKey('devices.IDdevice'), nullable = False)
    event_set_state = db.Column(db.String(4), nullable = False)
    edgeID = db.Column(db.Integer, db.ForeignKey('edgestations.edgeID'))

    def __repr__(self):
        return f"Events(ID = {idee}, Event ID ={event_id}, Name = {event_name}, Condition Type = {event_condition_type}, Condition = {event_condition}, Device ID ={IDdevice}, State = {event_set_state}, Edge ID = {edgeID})"

#Readings Table
class ReadingsModel(db.Model):
    __tablename__ = 'readings'
    readingID = db.Column(db.Integer, primary_key = True)
    IDdevice = db.Column(db.Integer, nullable = False)
    device_ip = db.Column(db.String(19), nullable = False)
    weight = db.Column(db.Float, nullable = False)
    distance = db.Column(db.Float, nullable = False)
    longitude = db.Column(db.String(20), nullable = False)
    latitude = db.Column(db.Float, nullable = False)
    accuracy = db.Column(db.Float, nullable = False)
    timestamp = db.Column(db.Float, nullable = False)

    def __repr__(self):
        return f"Readings(ID = {readingID}, device ID = {IDdevice}, device ip = {device_ip}, weight = {weight}, distance = {distance}, longitude = {longitude}, latitude = {latitude}, accuracy = {accuracy}, timestamp = {timestamp})"

#Predictions Table
class PredictionsModel(db.Model):
    __tablename__ = 'predictions'
    prediction_id = db.Column(db.Integer, primary_key = True)
    prediction = db.Column(db.String(10), nullable = False)
    result = db.Column(db.String(10), nullable = True)
    application_name = db.Column(db.String(30), nullable = False)
    readingID = db.Column(db.Integer, db.ForeignKey('readings.readingID'), nullable = False)

    def __repr__(self):
        return f"Predictions(ID = {prediction_id}, prediction = {prediction}, result = {result}, application = {application_name}, reading ID = {readingID}"
 

#device request parsers
devices_put_args = reqparse.RequestParser()
devices_put_args.add_argument("name", type=str, help="Name of device is required", required=True)
devices_put_args.add_argument("device_type", type=str, help="Type of device is required", required=True)
devices_put_args.add_argument("deviceID", type=int, help="ID of device is required", required=True)

device_update_args = reqparse.RequestParser()
device_update_args.add_argument("name", type=str, help="Name of device is required")
device_update_args.add_argument("device_type", type=str, help="Type of device is required")

#edge station request parsers
edge_put_args = reqparse.RequestParser()
edge_put_args.add_argument("edge_name", type=str, help="Name of edge is required", required=True)
edge_put_args.add_argument("edge_ip", type=str, help="Edge IP is required", required=True)
edge_put_args.add_argument("edegeID", type=int, help="ID of device is required", required=True)

edge_update_args = reqparse.RequestParser()
edge_update_args.add_argument("edge_name", type=str, help="Name of edege is required")
edge_update_args.add_argument("device_ip", type=str, help="IP of device is required")


device_fields = {
    'IDdevice' : fields.Integer,
    'name' : fields.String,
    'device_type': fields.String,
    'device_edgeID' : fields.Integer
}


edgestation_fields = {
    'edgeID' : fields.Integer,
    'edge_name' : fields.String,
    'edge_ip' : fields.String,
    'edge_port' : fields.Integer
}

events_field = {
    'idee': fields.Integer,
    'event_id' : fields.Integer,
    'event_name' : fields.String,
    'event_condition_type' : fields.Float,
    'event_condition' : fields.String,
    'IDdevice' : fields.Integer,
    'event_set_state' : fields.String,
    'edgeID' :fields.Integer
}

readings_field = {
    'readingID' : fields.Integer,
    'IDdevice' : fields.Integer,
    'device_ip' : fields.String,
    'weight' : fields.Float,
    'distance' : fields.Float,
    'longitude' : fields.String,
    'latitude' : fields.Float,
    'accuracy' : fields.Float,
    'timestamp' : fields.Float
}

predictions_field = {
    'prediction_id' : fields.Integer,
    'prediction' : fields.String,
    'result' : fields.String,
    'application_name' : fields.String,
    'readingID' : fields.Integer
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

class ReturnEvents(Resource):
    @marshal_with(events_field)
    def get(self):
        result = EventsModel.query.all()
        return result

class ReturnReadings(Resource):
    @marshal_with(readings_field)
    def get(self):
        result = ReadingsModel.query.all()
        return result

class ReturnPredictions(Resource):
    @marshal_with(predictions_field)
    def get(self):
        result = PredictionsModel.query.all()
        return result

@app.route("/devices/add-new")
def addDevice():

    return "<h1> Add a new device here <h1>"



api.add_resource(ReturnEdgeStations, '/edgestations')
api.add_resource(ReturnDevices, '/devices')
api.add_resource(ReturnEvents, '/events')
api.add_resource(ReturnPredictions, '/predictions')
api.add_resource(ReturnReadings, '/readings')

if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = 8080, debug = True)

