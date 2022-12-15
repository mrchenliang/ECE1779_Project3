from glob import glob
from flask import Flask, render_template, g
from api import api_routes
from image import image_routes
from manager import manager_routes
from stats import stat_routes

webapp = Flask(__name__)
webapp.register_blueprint(api_routes)
webapp.register_blueprint(image_routes)
webapp.register_blueprint(manager_routes)
webapp.register_blueprint(stat_routes)

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
    return render_template('main.html')

@webapp.errorhandler(404)
# returns the 404 page
def page_not_found(e):
    return render_template('404.html'), 404

@webapp.errorhandler(500)
# returns the 500 page
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    webapp.run('0.0.0.0',5000,debug=True,threaded=True)
