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

    def __init__(self, url_base, login_path):
        self.url_base = url_base
        self.login_path = login_path

    def request(self, path, method='get', **kwargs):
        '''
        request(path, method='get/post/put/delete', body={})
        returns a request result (python-requests)
        '''
        _method = method.lower()

        hdrs = {}
        if 'headers' in kwargs:
            hdrs = kwargs.pop('headers')

        if isinstance(strapi_session.get('jwt'), str):
            jwt = strapi_session.get('jwt')
            if 'Authorization' not in hdrs:
                hdrs['Authorization'] = f'Bearer {jwt}'

        url = f'{self.url_base}{path}'
        try:
            if _method in ['post', 'put', 'delete']:
                res = getattr(requests, _method)(url, headers=hdrs, **kwargs)
            else:
                # default to get request
                res = requests.get(url, headers=hdrs, **kwargs)

            return res
        except requests.exceptions.ConnectionError:
            raise requests.exceptions.ConnectionError('ConnectionError: connection to strapi cms failed')
        except requests.exceptions.Timeout:
            raise requests.exceptions.ConnectionError('Timeout: timeout error on request to strapi cms')

    def authenticate(self, username, password):
        '''
        authenticate(username, password)
        returns True if successfuly, False otherwise
        '''
        res = self.request(self.login_path, method='post', json={'identifier': username, 'password': password})
        if res.status_code == 200:
            _set_strapi_session(res)
            return None
        return res

class StrapiV3(Strapi):
    def __init__(self, url_base = 'http://localhost:1337', login_path='/auth/local'):
        super.__init__(url_base, login_path)

class StrapiV4(Strapi):

    def __init__(self, url_base = 'http://localhost:1337', login_path='/api/auth/local'):
        super.__init__(url_base, login_path)
