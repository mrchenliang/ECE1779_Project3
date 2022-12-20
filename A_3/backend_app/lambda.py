import boto3
import json

lambda_client = boto3.client('lambda',
                             region_name='us-east-1',)
data = {"test": "test"}

response = lambda_client.invoke(FunctionName="cloudwatch",
                                InvocationType="Event",         ###for asynchronous purposes
                                Payload=json.dumps(data)
                                )