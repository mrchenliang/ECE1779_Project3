import boto3
from constants import default_max_capacity, default_replacement_policy

dynamodb = boto3.resource('dynamodb')
cache_properties = dynamodb.Table('cache_properties')

def get_cache():
    # get the cache properties from the database cache_properties
    try:
        response = cache_properties.get_item(
            Key={
                    'policy_number' : 1,
                }
        )
        if 'Item' in response:
            cache = response['Item']
            max_capacity = cache['max_capacity']
            replacement_policy = cache['replacement_policy']
            return max_capacity, replacement_policy
        return default_max_capacity, default_replacement_policy
    except:
        return None

def set_cache(max_capacity, replacement_policy):
    # put new cache properties into the database cache_properties
    try:

        response = cache_properties.put_item(
        Item={
                'policy_number': 1,
                'max_capacity': max_capacity,
                'replacement_policy': replacement_policy,
            }
        )
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
    except:
        return None
