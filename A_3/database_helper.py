from flask import g
import mysql.connector
import os, requests, json
db_config = {'user': 'admin',
             'password': 'ece1779group2',
             'host': 'briandatabase.cls58pggr43c.us-east-1.rds.amazonaws.com',
             'port': '3306',
             'database': 'memcache'
            }

def connect_to_database():
    # connect to the database
    return mysql.connector.connect(user=db_config['user'],
                                   password=db_config['password'],
                                   host=db_config['host'],
                                   port=db_config['port'],
                                   database=db_config['database'])    
