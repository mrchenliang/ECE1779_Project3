import base64, os, requests, boto3, tempfile, json
from botocore.config import Config
# from frontend.image import s3_storage_helper
from database_helper import get_db

config = Config(
    region_name = 'us-east-1',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)

# s3 = boto3.client('s3',config=config, aws_access_key_id= aws_config['aws_access_key_id'], aws_secret_access_key= aws_config['aws_secret_access_key'])
s3 = boto3.client('s3',config=config)
rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')
images = dynamodb.Table('images')

memcache_host = "http://0.0.0.0:5001"
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif'}
ALLOWED_IMAGES = ['Graffiti', 'Art']

def download_image(key):
    try: 
        with open('Temp.txt', 'wb') as file:
            s3.download_fileobj('briansbucket', key, file)
        with open('Temp.txt', 'rb') as file:
            base64_image = file.read().decode('utf-8')
        file.close()
        os.remove("Temp.txt")
        return base64_image
    except:
        return 'Image Not Found in S3'

def process_image(request, key):
    global memcache_host
    # get the image file
    file = request.files['file']
    _, extension = os.path.splitext(file.filename)
    # if the image is one of the allowed extensions
    if extension.lower() in ALLOWED_EXTENSIONS:
        if check_image_rekognition(file) == True:
            filename = key + extension
            # save the image in the s3
            print('uploading')

            base64_image = base64.b64encode(file.read())
            try:
                s3.put_object(Body=base64_image, Key=key, Bucket='briansbucket', ContentType='image')
                print("uploaded")
            except:
                return "INVALID"

            
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
    global memcache_host
    try:
        # get the image file
        file = request.files['file']
        _, extension = os.path.splitext(file.filename)
        # if the image is one of the allowed extensions
        if extension.lower() in ALLOWED_EXTENSIONS:
            if check_image_rekognition(file) == True:
                filename = key + extension
                # save the image in the s3
                print("uploading")
                base64_image = base64.b64encode(file.read())
                try:
                    s3.put_object(Body=base64_image, Key=key, Bucket='briansbucket', ContentType='image')
                    print("uploaded")
                except:
                    return "INVALID"
                
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
    except:
        return "INVALID"

def check_image_rekognition(image):
    """
    Using this function to check if image is graffiti or art
    :param image: The uploading image file
    :return: bool
    """
    # Check if the object_name is given or not, if not, using the file_name as the object_name
    response = rekognition.detect_labels(Image={'Bytes': image.read()})

    labels = response['Labels']
    print(f'Found {len(labels)} labels in the image:')
    for label in labels:
      name = label['Name']
      confidence = label['Confidence']
      if name in ALLOWED_IMAGES and confidence > 80:
        return True
    return False
