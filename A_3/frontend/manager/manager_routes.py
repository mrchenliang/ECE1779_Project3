
from flask import Blueprint
import requests, time
from flask import render_template, request, redirect
from frontend.database_helper import get_db
from manager_helper import get_cache, set_cache

manager_routes = Blueprint("manager_routes", __name__)

@manager_routes.route('/memcache_manager', methods=['GET'])
def memcache_manager():
    max_capacity, replacement_policy, created_at = get_cache()
    return render_template('manager.html',
        max_capacity=max_capacity,
        replacement_policy=replacement_policy,
        created_at=created_at)

@manager_routes.route('/set_cache', methods = ['GET', 'POST'])
def memcache_properties():
    if request.method == 'POST':
        new_capacity = request.form.get('max_capacity')
        if new_capacity.isdigit() and int(new_capacity) <= 2000:
            new_policy = request.form.get('replacement_policy')
            req = {
                'max_capacity': new_capacity, 
                'replacement_policy': new_policy, 
            }
            resp = requests.post(backend_host + '/refresh_configuration', json=req)
            max_capacity, replacement_policy, created_at = get_cache()
            print(resp.json())
            if resp.json() == 'OK':
                return render_template('manager.html',
                max_capacity=max_capacity,
                replacement_policy=replacement_policy,
                created_at=created_at)
             
        # On error, reset to old params
        max_capacity, replacement_policy, created_at = get_cache()
        return render_template('manager.html',
                max_capacity=max_capacity,
                replacement_policy=replacement_policy,
                created_at=created_at,
                status="TRUE")
        
    # On GET
    max_capacity, replacement_policy, created_at = get_cache()
    return render_template('manager.html',
            max_capacity=max_capacity,
            replacement_policy=replacement_policy,
            created_at=created_at)

@manager_routes.route('/clear_cache', methods=['GET', 'POST'])
def clear_cache():
    global backend_host
    if request.method == 'POST':
        res = requests.post(backend_host + '/clear_cache_pool')
    max_capacity, replacement_policy, created_at = get_cache()
    return render_template('manager.html',
        max_capacity=max_capacity,
        replacement_policy=replacement_policy,
        created_at=created_at)

@manager_routes.route('/clear_data', methods=['GET', 'POST'])
def clear_data():
    global backend_host
    if request.method == 'POST':
        res = requests.post(backend_host + '/clear_data')
    max_capacity, replacement_policy, created_at= get_cache()
    return render_template('manager.html',
        max_capacity=max_capacity,
        replacement_policy=replacement_policy,
        created_at=created_at)


def get_cache():
    # get the cache properties from the database cache_properties
    try:
        cnx = get_db()
        cursor = cnx.cursor(buffered = True)
        query = '''SELECT * FROM cache_properties WHERE id = (SELECT MAX(id) FROM cache_properties LIMIT 1)'''
        cursor.execute(query)
        if(cursor._rowcount):
            cache=cursor.fetchone()
            return cache
        return None
    except:
        return None