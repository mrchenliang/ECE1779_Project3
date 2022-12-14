import base64, os, requests, boto3, tempfile, json
from botocore.config import Config
# from frontend.image import s3_storage_helper
from frontend.database_helper import get_db

config = Config(
    region_name = 'us-east-1',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)

# s3 = boto3.client('s3',config=config, aws_access_key_id= aws_config['aws_access_key_id'], aws_secret_access_key= aws_config['aws_secret_access_key'])
s3 = boto3.client('s3',config=config)
rekognition = boto3.client('rekognition', region_name="us-east-1")

memcache_host = "http://0.0.0.0:5001"
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif'}
ALLOWED_IMAGES = ['graffiti', 'art']

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
            s3.put_object(Body=base64_image, Key=key, Bucket='briansbucket', ContentType='image')
            print("uploaded")
            
            # post request to invalidate memcache by key
            request_json = {
                "key": key
            }
            # post request to invalidate memcache by key
            res = requests.post(memcache_host + '/invalidate_specific_key', json=request_json)
            # add the key and location to the database
            return add_image_to_db(key, filename)
        else:
            return 'INVALID'
    return 'INVALID'

def add_image_to_db(key, location):
    if key == '' or location == '':
        return 'FAILURE'
    try:
        # write to the database images with the key and location
        cnx = get_db()
        cursor = cnx.cursor(buffered = True)
        # check if the key already exists
        query_exists = 'SELECT EXISTS(SELECT 1 FROM images WHERE images.key = (%s))'
        cursor.execute(query_exists,(key,))
        # if it exists, delete the key and location
        for elem in cursor:
            if elem[0] == 1:
                query_delete = 'DELETE FROM images WHERE images.key=%s'
                cursor.execute(query_delete,(key,))
                break
        # write to the database images with the key and location
        query_insert = '''INSERT INTO images (images.key, images.location) VALUES (%s,%s);'''
        cursor.execute(query_insert,(key,location,))
        cnx.commit()
        cnx.close()
        return 'OK'
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
                s3.put_object(Body=base64_image, Key=key, Bucket='briansbucket', ContentType='image')
                print("uploaded")
                
                # post request to invalidate memcache by key
                request_json = {
                    "key": key
                }
                # post request to invalidate memcache by key
                res = requests.post(memcache_host + '/invalidate_specific_key', json=request_json)
                # add the key and location to the database
                return add_image_to_db(key, filename)
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

def clear_images():
    s3_clear = boto3.resource('s3',config=config)
    bucket = s3_clear.Bucket('briansbucket')
    bucket.objects.all().delete()
    return True