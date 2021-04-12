from flask import Flask, render_template, request, redirect
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from datetime import datetime
from flask_cors import CORS

import json
import boto3
import pymysql
import sys
sys.path.insert(1, '/Users/josh/Desktop/Capstone')
import secrets
import zipfile
import tarfile
import requests
import sagemaker

app = Flask(__name__)
api = Api(app)
CORS(app)
cors = CORS(app,resources = {
    r"/*":{
        "origins" : "*"
    }
})

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
    deviceName = db.Column(db.String(128), nullable = False, unique = True)
    deviceId = db.Column(db.Integer, primary_key = True)
    deviceType = db.Column(db.String(128), nullable = False)
    deviceIp = db.Column(db.String(128), nullable = False)
    edgeStationID = db.Column(db.Integer, db.ForeignKey('edgestations.edgeStationID'), nullable = False)
    #edgeStationID = db.relationship('EdgeStationsModel', backref = db.backref('posts', lazy = True))
    
    def __init__(self, deviceName, deviceType, deviceIp, edgeStationID):
        self.deviceName = deviceName
        self.deviceType = deviceType
        self.deviceIp = deviceIp
        self.edgeStationID = edgeStationID

    def __repr__(self):
        return f"Devices(deviceName = {deviceName}, device ID = {deviceId}, device type = {deviceType}, device ip = {deviceIp}, edge station = {edgeStationID})" 

#Edge Stations Table
class EdgeStationsModel(db.Model):
    __tablename__ = 'edgestations'
    edgeStationID = db.Column(db.Integer, primary_key = True)
    edgeName = db.Column(db.String(20), nullable = False, unique = True)
    edge_ip = db.Column(db.String(15), nullable = False)
    edge_port = db.Column(db.Integer, nullable = False)

    def __init__(self, edgeName, edge_ip, edge_port):
        self.edgeName = edgeName
        self.edge_ip = edge_ip
        self.edge_port = edge_port

    def __repr__(self):
        return f"EdgeStation('{self.edgeStationID}', '{self.edgeName}', '{self.edge_ip}', {self.edge_port}')"
 
#Events Table
class EventsModel(db.Model):
    __tablename__ = 'event'
    eventID = db.Column(db.Integer, primary_key = True, nullable = True, unique = True)
    event_name = db.Column(db.String(30), nullable = True, unique = True)
    event_condition_type = db.Column(db.String(50))
    event_condition = db.Column(db.Float)
    deviceId = db.Column(db.Integer, db.ForeignKey('devices.deviceId'), nullable = False)
    event_set_state = db.Column(db.String(4), nullable = False)
    edgeStationID = db.Column(db.Integer, db.ForeignKey('edgestations.edgeStationID'))

    def __repr__(self):
        return f"Events('{self.eventID}', '{self.event_name}', '{self.event_condition_type}', '{self.event_condition}', '{self.deviceId}', '{event_set_state}', '{edgeStationID}')"

#Readings Table
class ReadingsModel(db.Model):
    __tablename__ = 'readings'
    readingID = db.Column(db.Integer, primary_key = True)
    deviceIp = db.Column(db.String(30), nullable = False)
    capacity = db.Column(db.Float, nullable = False)
    longitude = db.Column(db.Float, nullable = False)
    latitude = db.Column(db.Float, nullable = False)
    timestamp = db.Column(db.String(30), nullable = False)

    def __init__(self, deviceIp, capacity, longitude, latitude, timestamp):
        self.deviceIp = deviceIp
        self.capacity = capacity
        self.longitude = longitude
        self.latitude = latitude
        self.timestamp = timestamp

    def __repr__(self):
        return f"Readings(ID = {readingID}, device ip = {deviceIp}, capacity = {capacity}, longitude = {longitude}, latitude = {latitude}, timestamp = {timestamp})"

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
devices_put_args.add_argument("deviceName", type=str, help="Name of device is required", required=True)
devices_put_args.add_argument("deviceType", type=str, help="Type of device is required", required=True)
devices_put_args.add_argument("deviceID", type=int, help="ID of device is required", required=True)

device_update_args = reqparse.RequestParser()
device_update_args.add_argument("deviceName", type=str, help="Name of device is required")
device_update_args.add_argument("deviceType", type=str, help="Type of device is required")

#edge station request parsers
edge_put_args = reqparse.RequestParser()
edge_put_args.add_argument("edgeName", type=str, help="Name of edge is required", required=True)
edge_put_args.add_argument("edge_ip", type=str, help="Edge IP is required", required=True)
edge_put_args.add_argument("edegeStationID", type=int, help="ID of device is required", required=True)

edge_update_args = reqparse.RequestParser()
edge_update_args.add_argument("edgeName", type=str, help="Name of edege is required")
edge_update_args.add_argument("deviceIp", type=str, help="IP of device is required")


device_fields = {
    'deviceId' : fields.Integer,
    'deviceName' : fields.String,
    'deviceType': fields.String,
    'deviceIp' : fields.String,
    'edgeStationID' : fields.Integer
}


edgestation_fields = {
    'edgeStationID' : fields.Integer,
    'edgeName' : fields.String,
    'edge_ip' : fields.String,
    'edge_port' : fields.Integer
}

events_field = {
    'idee': fields.Integer,
    'eventID' : fields.Integer,
    'event_name' : fields.String,
    'event_condition_type' : fields.Float,
    'event_condition' : fields.String,
    'deviceId' : fields.Integer,
    'event_set_state' : fields.String,
    'edgeStationID' :fields.Integer
}

readings_field = {
    'readingID' : fields.Integer,
    'deviceIp' : fields.String,
    'capacity' : fields.Float,
    'longitude' : fields.Float,
    'latitude' : fields.Float,
    'timestamp' : fields.String
}

predictions_field = {
    'prediction_id' : fields.Integer,
    'prediction' : fields.String,
    'result' : fields.String,
    'application_name' : fields.String,
    'readingID' : fields.Integer
}
db.create_all()

#Classes for each component
class Devices(Resource):
    @marshal_with(device_fields)
    def get(self, device_id):
        result = DeviceModel.query.filter_by(deviceId = device_id).first()
        if not result:
            abort(404, message = "Could not find device")
        return result
        
    @marshal_with(device_fields)
    def put(self, device_id):
        args = devices_put_args.parse_args()
        result = DeviceModel.query.filter_by(deviceId = device_id).first()
        if result:
            abort(409, message = "Device ID exists")
        device = DeviceModel(name = args['deviceName'], deviceId = device_id, deviceType = args['deviceType'])
        db.session.add(device)
        db.session.commit()
        return device, 201
    
    @marshal_with(device_fields) 
    def patch(self, device_id):
        args = device_update_args.parse_args()
        result = DeviceModel.query.filter_by(deviceId = device_id).first()
        if not result:
            abort(404, message = "No such device, update failed") 
        if args['deviceName']:
            result.name = args['deviceName']
        if args['deviceType']:
            result.deviceType = args['deviceType']

        db.session.commit()

        return result

class EdgeStation(Resource):
    @marshal_with(edgestation_fields)
    def get(self, edgestation_id):
        result = EdgeStationsModel.query.filter_by(edgeStationID = edgestation_id).first()
        if not result:
            abort(404, message = "No such edge station")
        return result
    
    @marshal_with(edgestation_fields)
    def put(self, edgestation_id):
        args = edge_put_args.parse_args()
        result = EdgeStationsModel.query.filter_by(edgeStationID = edgestation_id).first()
        if result:
            abort(409, message = "Edgestation already exists")
        edgestation = DeviceModel(edgeName = args['edgeName'], edgeStationID = edgestation_id, edge_ip = args['edge_ip'])
        db.session.add(edgestation)
        db.session.commit()
        return edgestation, 201

class Readings(Resource):
    @marshal_with(readings_field)
    def get(self, readingIp):
        readingID = ReadingsModel.readingID
        capacity = ReadingsModel.capacity
        result = ReadingsModel.query.filter_by(deviceIp = readingIp).order_by(readingID.desc()).first()
        if not result:
            abort(404, message = "No device with that ip")
        return result

class ReadingsIp(Resource): 
    @marshal_with(readings_fields)
    def get(self, readingIp):
        result = ReadingsModel.query.filter_by(deviceIp = readingIp).all()
        if not result:
            abort(404, message = "no device with that ip")

api.add_resource(ReadingsIp, '/readings/<string:readingIp>')
api.add_resource(Readings, '/readings/<string:deviceIp>/last')
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

@app.route('/devicecreation')
def deviceAdd():
    return render_template('put_devices.html')
@app.route("/addDevice", methods = ['POST'])
def addDevice():
    new_device = DeviceModel(request.form['deviceName'], request.form['deviceType'], request.form['deviceIp'], request.form['edgeStationID'])
    #this also creates and registers the device in the cloud storage 
    url = "https://jwn9lb7938.execute-api.us-east-2.amazonaws.com/test/registerDevice"
    aDevice = {
        "deviceName" : request.form['deviceName'],
        "deviceIP" : request.form['deviceIp'],
        "deviceType" : request.form['deviceType']
    }
    response = requests.request("PUT", url, data = aDevice)
    #stores the new device into the application database 
    db.session.add(new_device)
    db.session.commit()
    return redirect('/devices')

@app.route('/edgecreation')
def edgeAdd():
    return render_template('put_edges.html')
@app.route("/addEdge", methods = ['POST'])
def addEdge():
    new_edge = EdgeStationsModel(request.form['edgeName'], request.form['edge_ip'], request.form['edge_port'])
    db.session.add(new_edge)
    db.session.commit()
    return redirect('/edgestations')


api.add_resource(ReturnEdgeStations, '/edgestations')
api.add_resource(ReturnDevices, '/devices')
api.add_resource(ReturnEvents, '/events')
api.add_resource(ReturnPredictions, '/predictions')
api.add_resource(ReturnReadings, '/readings')


#s3 Get Trained Model File from cloud bucket
s3 = boto3.client("s3")
path = '/home/ubuntu/smart-city-iot-platform-application/models/'
sagemaker_session = sagemaker.Session()

@app.route('/getTrainedModel', methods = ["GET"])
def getTrainedModel():
    bucket = 'sagemaker-us-east-2-583938224360'
    filePath = 'smartcity-waste-management-garbage-level-training-data/output/garbage-bin-level-forecaster-2021-02-16-16-57-57-804/output/model.tar.gz'

    try:
        response = s3.get_object(Bucket = bucket, Key = filePath)
        payload = response['Body'].read()
        downloadPayload = s3.download_file(bucket, filePath, path + 'model.tar.gz')
        #print(open('model.zip').read())
        tf = tarfile.open(path + 'model.tar.gz')
        tf.extractall(r'/home/ubuntu/smart-city-iot-platform-application/models/model')
        
        return{
            'response_code' : 200,
            'message' : 'Succesffuly downloaded the model file from the cloud.'
        }
    except Exception as e:
        return{
            'response_code' : 404,
            'message' : repr(e)
        }

# get the devices readings from lambda
@app.route('/deviceReadings', methods = ["POST"])
def putDeviceReadings():
    req = request.get_json()
    readingApplicationName = req['applicationName']
    readingEdgeName = req['edgeName']
    readingDeviceType = req['deviceType']
    readingDeviceName = req['deviceName']
    readingDeviceIp = req['deviceIP']
    readingCapacity = req['capacity']
    readingLongitude = req['longitude']
    readingLatitude = req['latitude']
    readingTimestamp = req['timestamp']
    
    newReading = ReadingsModel(readingDeviceIp, readingCapacity, readingLongitude, readingLatitude, readingTimestamp)
    db.session.add(newReading)
    db.session.commit()
    return redirect('/readings')



@app.route('/modelTrainingTriggerHandler', methods = ['GET'])
def sendEvent():
    dt = datetime.now()
    now = dt.strftime('%Y-%m-%d-%H-%M-%S')
    url = "https://jwn9lb7938.execute-api.us-east-2.amazonaws.com/test/modelTrainingTriggerHandler"
    config = {
        "freq" : "10S",
        "training_job_name" : "garbage-bin-level-forecaster-" + now,
        "context_length" : 60480,
        "s3_bucket_name" : "sagemaker-us-east-2-583938224360",
        "s3_bucket_application_base_uri" : "smartcity-waste-management-garbage-level-training-data",
        "prediction_length" : 60480,
        'arn_role': 'arn:aws:iam::583938224360:role/sagemakerfullaccess'
    }
    send = requests.post(url, json = config )
    sagemaker_session = sagemaker.Session()
    sagemaker_session.wait_for_job(config['training_job_name'])
    
    print('Creating an endpoint using \'', config['training_job_name'], '\' as the training job')
    endpoint_name = sagemaker_session.endpoint_from_job(
        job_name=config['training_job_name'],
        initial_instance_count=1,
        instance_type='ml.m4.xlarge',
        role=config['arn_role']
    )
    # once the endpoint has been created, make the predictor object and save it to be reused later when a prediction is needed
    print('\nEndpoint has been created with the following name ', endpoint_name)
    predictor = sagemaker.predictor.Predictor(
        endpoint_name,
        sagemaker_session=sagemaker_session,
        serializer=sagemaker.serializers.IdentitySerializer(content_type='application/json')
    )
    final = print(send)
    return config

def predict(predictor):
    ts = [1,2,3]
    instance = {
        'start' : '2014-01-01 00:00:00',
        'target' : ts
    }
    data = {'instances': [instance]}
    request = json.dumps(data).encode('utf-8')
    prediction = json.loads(predictor.predict(request).decode('utf-8'))
    predictor.delete_endpoint()




if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = 8080, debug = True)

