from flask import Flask
from frontend.api import api_routes
from frontend.image import image_routes
from frontend.manager import manager_routes
from frontend.stat import stat_routes


webapp = Flask(__name__)
webapp.register_blueprint(api_routes)
webapp.register_blueprint(image_routes)
webapp.register_blueprint(manager_routes)
webapp.register_blueprint(stat_routes)