from datetime import datetime
import json
import requests

x = datetime.now()
print(type(x))

now =x.strftime('%Y-%m-%d-%H-%M-%S')

url = "https://jwn9lb7938.execute-api.us-east-2.amazonaws.com/test/modelTrainingTriggerHandler"
data = {
    "freq" : "10S",
    "training_job_name" : "garbage-bin-level-forecaster-" + now,
    "context_length" : 60480,
    "s3_bucket_name" : "sagemaker-us-east-2-583938224360",
    "s3_bucket_application_base_uri" : "smartcity-waste-management-garbage-level-training-data",
    "prediction_length" : 60480
}
send = requests.post(url, json = data )
print(send)