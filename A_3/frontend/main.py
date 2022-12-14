from glob import glob
from flask import Flask, render_template, g
# from frontend.constants import default_max_capacity, default_replacement_policy
# from frontend.manager.manager_helper import set_cache
from frontend import webapp

# @webapp.before_first_request
# # initialize the cache configuration settings on first startup
# def set_cache_config_settings():
#     set_cache(default_max_capacity, default_replacement_policy)

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
