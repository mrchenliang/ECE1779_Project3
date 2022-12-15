from flask import Blueprint, jsonify, render_template, request, send_file, redirect
from image.image_helper import *
from constants import memcache_host
import requests

image_routes = Blueprint('image_routes', __name__)

@image_routes.route('/upload_image', methods = ['GET','POST'])
# returns the upload page
def upload_image():
    if request.method == 'POST':
        key = request.form.get('key')
        # process the upload image request and add the image to the database
        status = process_image(request, key)
        return render_template('upload_image.html', status=status)
    return render_template('upload_image.html')

@image_routes.route('/get_image/<string:image>')
# returns the actual image
def get_image(image):
    filepath = 'static/images/' + image
    return send_file(filepath)

@image_routes.route('/image', methods = ['GET','POST'])
# returns the view image page
def image():
    if request.method == 'POST':
        key_value = request.form.get('key_value')
        # get the image by key from the memcache
        request_json = {
            'key': key_value
        }
        res = requests.post(memcache_host + '/get_from_memcache', json=request_json)
        # if the image is not by the key in the memcache
        if res.text == 'Key Not Found' or res == None:
            # queries the database images by specific key
            try:
                response = images.get_item(
                Key = {
                        'key' : key_value,
                    }
                )
                if 'Item' in response:
                    image = download_image(key_value)
                    if image == 'Image Not Found in S3':
                        return render_template('image.html', exists=False, image='does not exist')
                    request_json = { 
                        key_value: image 
                    }
                    # put the key and image into the memcache
                    res = requests.post(memcache_host + '/put_into_memcache', json=request_json)
                    # returns view image page
                    return render_template('image.html', exists=True, image=image)
            except:
                return render_template('image.html', exists=False, image='does not exist')

            else:
                return render_template('image.html', exists=False, image='does not exist')
        else:
            # returns view image page
            return render_template('image.html', exists=True, image=res.text)
    return render_template('image.html')

@image_routes.route('/keys_list', methods=['GET'])
# returns the webpage list of keys page
def keys_list():
    # queries the database images for a list of keys
    try:
        response = images.scan()
        keys = []
        for item in response['Items']:
            keys.append(item['key'])
        if keys:
            return render_template('keys_list.html', keys=keys, length=len(keys))
        else:
            return render_template('keys_list.html')
    except:
        return render_template('keys_list.html')