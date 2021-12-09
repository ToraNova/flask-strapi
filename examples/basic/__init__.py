'''
this examples assumes the following:
1. strapi app from https://github.com/strapi/foodadvisor is running on localhost:1337

how to run?
from flask-strapi project root, do:
export FLASK_APP=examples/basic
export FLASK_ENV=development
flask run
or
flask run --no-reload (no reloading)
'''

import secrets
import re
import requests
from flask import Flask, render_template, redirect, url_for, request, flash, session, abort
from flask_strapi import Strapi, strapi_session, clear_strapi_session, authentication_required

def create_app():

    # create flask app
    app = Flask(__name__, instance_relative_config=True, )
    # do not use in workers
    app.secret_key = secrets.token_urlsafe(32)
    app.testing = False

    cms = Strapi(url_base = 'http://localhost:1337')

    @app.route('/')
    def root():
        return redirect(url_for('login'))

    @app.route('/logout')
    def logout():
        session.pop('strapi', None)
        flash('logout success', 'ok')
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET' ,'POST'])
    def login():
        if strapi_session:
            clear_strapi_session()
            # clear login session if head to login again

        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            err = cms.authenticate(username, password)
            if not err:
                return redirect(url_for('home'))
            flash(f'error {err}', 'err')

        return render_template('login.html')

    @app.route('/home')
    @authentication_required
    def home():
        user = strapi_session.get('user')
        username = user.get('username')
        return f'logged in as {username}'

    @app.route('/test/find')
    @authentication_required
    def test_find():
        # or any other content, remember to ensure that the user has permission
        # to 'find' the content
        res = cms.request('/reviews')
        return str(res)

    @app.route('/test/find_one/<int:id>')
    @authentication_required
    def test_find_one(id):
        # or any other content, remember to ensure that the user has permission
        # to 'find' the content
        res = cms.request(f'/reviews/{id}')
        print(res)
        return str(res)

    @app.route('/test/create')
    @authentication_required
    def test_create():
        user = strapi_session.get('user')
        res = cms.request('/reviews', 'post', {
            'content': 'this is a test',
            'note': 3,
            'author': user.get('id'),
            'restaurant': 15
        })
        return str(res)

    @app.route('/test/update/<int:note>')
    @authentication_required
    def test_update(note):
        user = strapi_session.get('user')
        res = cms.request('/reviews/171', 'put', {
            'content': 'this is a test',
            'note': note,
            'author': user.get('id'),
            'restaurant': 15
        })
        return str(res)

    @app.route('/test/delete/<int:id>')
    @authentication_required
    def test_delete(id):
        res = cms.request(f'/reviews/{id}', 'delete')
        return str(res)

    return app
