from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
@app.route("/")


class DeviceModel(db.Model):
    __tablename__ = 'devices'
    name = db.Column(db.String(20), nullable = False, unique = True)
    IDdevice = db.Column(db.Integer, primary_key = True)
    device_type = db.Column(db.String(20), nullable = False)
    #edgeID = db.Column(db.Integer, db.ForeignKey('edgestations.edgeID'), nullable = False)
    #edgestations = db.relationship('EdgeStationsModel', backref = db.backref('posts', lazy = True))


    def __repr__(self):
        return f"Devices(name ={name}, deviceID = {IDdevice}, device_type = {device_type}) " 
'''
class EdgeStationsModel(db.Model):
    __tablename__ = 'edge_stations'
    edgeID = db.Column(db.Integer, primary_key = True)
    edge_name = db.Column(db.String(20), nullable = False)
    edge_ip = db.Column(db.String(15), nullable = False)
    edge_port = db.Column(db.Integer, nullable = False)

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
    'device_type': fields.String
}

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


'''
class EdgeStation():
    def get(self, edgestation_id):
        result = EdgeStationsModel.query.get(edgestation_id = edgestation_id)
'''
api.add_resource(Devices, '/devices/<int:device_id>')



if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = 8080, debug = True)

