import boto3
import json, requests, time

lambda_client = boto3.client('lambda',
                             region_name='us-east-1',)
data = {"test": "test"}

response = lambda_client.invoke(FunctionName="cloudwatch",
                                InvocationType="Event",         ###for asynchronous purposes
                                Payload=json.dumps(data)
                                )

url = "https://msiadrxh4hg334bvmxhs7n6ija0jqwog.lambda-url.us-east-1.on.aws/ "
while True:
    res = requests.get(url, params=data)
    time.sleep(5)