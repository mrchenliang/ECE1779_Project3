import mysql.connector
from flask import g
from constants import db_config

def connect_to_database():
    # connect to the database
    return mysql.connector.connect(user='admin',
                                   password='ece1779group2',
                                   host='briandatabase.cls58pggr43c.us-east-1.rds.amazonaws.com',
                                   port='3306',
                                   database='briandatabase')

def get_db():
    # get the database
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db
    
