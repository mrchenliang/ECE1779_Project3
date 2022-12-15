import boto3

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
            max_capacity = cache[0]
            replacement_policy = cache[1] 
            return max_capacity, replacement_policy
        return None
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
