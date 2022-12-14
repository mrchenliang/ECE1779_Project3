from glob import glob
from flask import Flask, render_template, g, request, redirect, url_for
from frontend.api import api_routes
from frontend.image import image_routes
from frontend.manager import manager_routes
from frontend.stat import stat_routes
import json

webapp = Flask(__name__)
webapp.register_blueprint(api_routes)
webapp.register_blueprint(image_routes)
webapp.register_blueprint(manager_routes)
webapp.register_blueprint(stat_routes)


global pool_notification
pool_notification = ""

@webapp.teardown_appcontext
# close out the db connection on shutdown
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@webapp.route('/')
@webapp.route('/home')
# returns the main page
def home():
    global pool_notification
    return render_template('main.html', pool_notification=pool_notification)

@webapp.errorhandler(404)
# returns the 404 page
def page_not_found(e):
    return render_template('404.html'), 404

@webapp.errorhandler(500)
# returns the 500 page
def internal_server_error(e):
    return render_template('500.html'), 500
