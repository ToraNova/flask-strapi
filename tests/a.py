import pytest

from examples.basic import create_app

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app({"TESTING": True})

    # create the database and load test data
    with app.app_context():
        pass

    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

def test_run(client):
    '''main test'''

    rv = client.get('/')
    assert rv.status_code == 302 #redirected

    rv = client.get('/treasure')
    assert rv.status_code == 401
    assert b'<h1>not logged in</h1>' in rv.data

    rv = client.get('/basic/login')
    assert rv.status_code == 200

    rv = client.get('/basic/profile')
    assert rv.status_code == 401

    rv = client.get('/basic/logout')
    assert rv.status_code == 302

    rv = client.post('/basic/login', data=dict(username='jason', password='test'), follow_redirects = True)
    assert rv.status_code == 401

    rv = client.post('/basic/login', data=dict(username='ting', password='hello'), follow_redirects = True)
    assert rv.status_code == 200
    assert b'hello ting' in rv.data

    rv = client.get('/treasure')
    assert rv.status_code == 200
    assert b'you got the treasure' in rv.data

    rv = client.get('/basic/logout', follow_redirects = True)
    assert rv.status_code == 200
    assert b'test with kwarg 123' in rv.data # kwargs test

    rv = client.get('/treasure')
    assert rv.status_code == 401
    assert b'<h1>not logged in</h1>' in rv.data
