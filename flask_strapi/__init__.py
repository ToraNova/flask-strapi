import requests
import sys, traceback
from flask import session, abort, has_request_context
from werkzeug.local import LocalProxy
from functools import wraps

strapi_session = LocalProxy(lambda: _get_strapi_session())

def clear_strapi_session():
    '''
    clears the strapi session (i.e., for logging out)
    '''
    session.pop('strapi', None)

def has_strapi_session():
    '''
    return true if a strapi session is established
    '''
    if has_request_context():
        return session.get('strapi') is not None
    return False

def _get_strapi_session():
    '''
    proxy method to get strapi session,
    return None if no strapi session exists
    '''
    return session.get('strapi') if session.get('strapi') else None

def authentication_required(fn):
    '''
    wrapper to automatically abort(401) if no strapi session is established
    '''
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        if not has_strapi_session():
            abort(401)
        return fn(*args, **kwargs)
    return decorated_view

class Strapi:

    def __init__(self, url_base, login_path):
        self.clear_app_session()
        self.url_base = url_base
        self.login_path = login_path

    def request(self, path, method='get', as_app_session=False, **kwargs):
        '''
        request(path, method='get/post/put/delete', body={})
        returns a request result (python-requests)
        '''
        _method = method.lower()

        hdrs = {}
        if 'headers' in kwargs:
            hdrs = kwargs.pop('headers')

        jwt = None
        if has_strapi_session():
            # allow usage outside of request context
            jwt = strapi_session['jwt']
        elif as_app_session:
            jwt = self.app_session['jwt']

        if jwt is not None and 'Authorization' not in hdrs:
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

    def authenticate(self, username, password, as_app_session=False):
        '''
        authenticate(username, password)
        returns True if successfuly, False otherwise
        '''
        res = self.request(self.login_path, method='post', json={'identifier': username, 'password': password})
        if res.status_code == 200:
            rj = res.json()
            if has_request_context() and not as_app_session:
                session['strapi'] = rj
            else:
                self.app_session = rj
            return None
        return res

    def clear_app_session(self):
        self.app_session = None

class StrapiV3(Strapi):
    def __init__(self, url_base = 'http://localhost:1337', login_path='/auth/local'):
        super.__init__(url_base, login_path)

class StrapiV4(Strapi):

    def __init__(self, url_base = 'http://localhost:1337', login_path='/api/auth/local'):
        super.__init__(url_base, login_path)
