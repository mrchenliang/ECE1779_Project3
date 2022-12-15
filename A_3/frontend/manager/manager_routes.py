
from flask import Blueprint
import requests, time
from flask import render_template, request
from manager.manager_helper import get_cache, set_cache

manager_routes = Blueprint("manager_routes", __name__)
memcache_host = "http://0.0.0.0:5001"

@manager_routes.route('/memcache_manager', methods=['GET'])
def memcache_manager():
    max_capacity, replacement_policy = get_cache()
    return render_template('manager.html',
        max_capacity=max_capacity,
        replacement_policy=replacement_policy)

@manager_routes.route('/set_cache', methods = ['GET', 'POST'])
def memcache_properties():
    if request.method == 'POST':
        new_capacity = request.form.get('max_capacity')
        if new_capacity.isdigit() and int(new_capacity) <= 2000:
            new_policy = request.form.get('replacement_policy')
            set_cache(new_capacity, new_policy)
            max_capacity, replacement_policy = get_cache()
            req = {
                'max_capacity': max_capacity, 
                'replacement_policy': replacement_policy, 
            }
            resp = requests.post(memcache_host + '/refresh_configuration', json=req)
            print(resp.json())
            if resp.json() == 'OK':
                return render_template('manager.html',
                max_capacity=max_capacity,
                replacement_policy=replacement_policy)
             
        # On error, reset to old params
        max_capacity, replacement_policy = get_cache()
        return render_template('manager.html',
                max_capacity=max_capacity,
                replacement_policy=replacement_policy,
                status="TRUE")
        
    # On GET
    max_capacity, replacement_policy = get_cache()
    return render_template('manager.html',
            max_capacity=max_capacity,
            replacement_policy=replacement_policy)

@manager_routes.route('/clear_cache', methods=['GET', 'POST'])
def clear_cache():
    global memcache_host
    if request.method == 'POST':
        res = requests.post(memcache_host + '/clear_cache')
    max_capacity, replacement_policy = get_cache()
    return render_template('manager.html',
        max_capacity=max_capacity,
        replacement_policy=replacement_policy,
        status="CLEAR")