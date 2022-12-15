import os, requests, json
# resp = requests.get("http://169.254.169.254/latest/user-data")
# config = json.loads(resp.content.decode('utf-8'))

# aws_config = {
#   'aws_access_key_id': config['aws_access_key_id'],
#   'awss_secret_access_key': config['aws_secret_access_key']
# }

db_config = {'user': 'admin',
             'password': 'ece1779group2',
             'host': "briandatabase.cls58pggr43c.us-east-1.rds.amazonaws.com",
             'port': '3306',
             'database': 'memcache'
            }

ALLOWED_IMAGES = ['graffiti', 'art']


default_max_capacity = 10
default_replacement_policy = 'Least Recently Used'
