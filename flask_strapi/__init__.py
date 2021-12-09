import requests
import sys, traceback
from flask import session, abort
from werkzeug.local import LocalProxy
from functools import wraps

strapi_session = LocalProxy(lambda: _get_strapi_session())
null_session = LocalProxy(lambda: _get_null_session())

def clear_strapi_session():
    _pop_strapi_session()

def _get_strapi_session():
    return session.get('strapi') if session.get('strapi') else null_session

def _get_null_session():
    return {'jwt': None, 'user': {}}

def _set_strapi_session(res):
    j = res.json()
    session['strapi'] = j

def _pop_strapi_session():
    session.pop('strapi', None)

def authentication_required(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        if strapi_session.get('jwt') is None:
            abort(401)
        return fn(*args, **kwargs)
    return decorated_view

class Strapi:

    def __init__(self, url_base = 'http://localhost:1337', login_path='/auth/local'):
        self.url_base = url_base
        self.login_path = login_path
        self.login_url = f'{self.url_base}{self.login_path}'

    def request(self, path, method='get', body={}):
        if strapi_session.get('jwt') is None:
            return {'statusCode':401, 'error':'Unauthorized', 'message':'session not established.'}

        jwt = strapi_session.get('jwt')
        url = f'{self.url_base}{path}'
        try:
            if method == 'post':
                res = requests.post(url, headers={'Authorization':f'Bearer {jwt}'}, json=body)
            elif method == 'put':
                res = requests.put(url, headers={'Authorization':f'Bearer {jwt}'}, json=body)
            elif method == 'delete':
                res = requests.delete(url, headers={'Authorization':f'Bearer {jwt}'})
            else:
                res = requests.get(url, headers={'Authorization':f'Bearer {jwt}'})

            if res.status_code == 404:
                return {'statusCode':404, 'error':'Not Found', 'message':'requested resources does not exist.'}

            return res.json()
        except requests.exceptions.ConnectionError:
            return {'statusCode':500, 'error':'ConnError', 'message':'connection error on request.'}
        except requests.exceptions.Timeout:
            return {'statusCode':408, 'error':'Timeout', 'message':'timeout error on request.'}
        except Exception as e:
            print(e) # print exception to console
            traceback.print_exc(file=sys.stdout)
            return {'statusCode':500, 'error':'Unexpected', 'message':'unexpected error has occurred.'}

    def authenticate(self, username, password):
        try:
            res = requests.post(self.login_url, json={'identifier': username, 'password':password})
            if res.status_code == 200:
                # success
                _set_strapi_session(res)
                return None
            else:
                # fail
                return 'invalid login.'
        except requests.exceptions.ConnectionError:
            return 'login request connection error.'
        except requests.exceptions.Timeout:
            return 'login request timeout.'
        except Exception as e:
            print(e) # print exception to console
            return 'unexpected error.'
