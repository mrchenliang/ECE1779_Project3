import base64, os, requests, boto3
from botocore.config import Config
from constants import memcache_host

config = Config(
    region_name = 'us-east-1',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)

s3 = boto3.client('s3',config=config)
rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')
images = dynamodb.Table('images')

ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif'}
ALLOWED_IMAGES = ['Graffiti', 'Art']

def download_image(key):
    try: 
        base64_image = s3.get_object(Bucket='pics1779', Key=key)["Body"].read().decode('utf-8')
        return base64_image
    except:
        return 'Image Not Found in S3'

def process_image(request, key):
    # get the image file
    file = request.files['file']
    file_bytes = file.read()
    _, extension = os.path.splitext(file.filename)
    # if the image is one of the allowed extensions
    if extension.lower() in ALLOWED_EXTENSIONS:
        if check_image_rekognition(file_bytes) == True:
            filename = key + extension
            print('uploading')
            base64_image = base64.b64encode(file_bytes)
            s3.put_object(Body=base64_image, Bucket='pics1779', Key=key)
            print("uploaded")

            # post request to invalidate memcache by key
            request_json = {
                "key": key
            }
            # post request to invalidate memcache by key
            res = requests.post(memcache_host + '/invalidate_specific_key', json=request_json)
            # add the key and location to the database
            return write_dynamo(key, filename)
        else:
            return 'INVALID'
    return 'INVALID'

def write_dynamo(key, location):
    if key == '' or location == '':
        return 'FAILURE'
    try: 
        response = images.put_item(
        Item={
                'key': key,
                'location': location,
            }
        )
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return "OK"
    except:
        return 'FAILURE'

def save_image(request, key):
    # get the image file
    file = request.files['file']
    file_bytes = file.read()
    _, extension = os.path.splitext(file.filename)
    # if the image is one of the allowed extensions
    if extension.lower() in ALLOWED_EXTENSIONS:
        if check_image_rekognition(file_bytes) == True:
            filename = key + extension
            # save the image in the s3
            print("uploading")
            base64_image = base64.b64encode(file_bytes)
            s3.put_object(Body=base64_image, Bucket='pics1779', Key=key)
            print("uploaded")
            
            # post request to invalidate memcache by key
            request_json = {
                "key": key
            }
            # post request to invalidate memcache by key
            res = requests.post(memcache_host + '/invalidate_specific_key', json=request_json)
            # add the key and location to the database
            return write_dynamo(key, filename)
        else:
            return 'INVALID'
    return 'INVALID'


def check_image_rekognition(image):
    """
    Using this function to check if image is graffiti or art
    :param image: The uploading image file
    :return: bool
    """
    # Check if the object_name is given or not, if not, using the file_name as the object_name
    response = rekognition.detect_labels(Image={'Bytes': image})

    labels = response['Labels']
    print(f'Found {len(labels)} labels in the image:')
    for label in labels:
      name = label['Name']
      confidence = label['Confidence']
      if name in ALLOWED_IMAGES and confidence > 80:
        return True
    return False
