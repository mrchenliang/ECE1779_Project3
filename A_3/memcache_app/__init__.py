from flask import Flask
from memcache_app import memcache
from memcache_app import config
webapp = Flask(__name__)

''' Default Type is LRU and default size is 10 MB'''
config.memcache_obj = memcache.LRUMemCache(10)

from memcache_app import memcache_routes