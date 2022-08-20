# flask-strapi
[![Build Status](https://travis-ci.org/ToraNova/flask-strapi.svg?branch=master)](https://travis-ci.org/ToraNova/flask-strapi)

A flask module to interact with Strapi CMS.

## Latest Changelogs
- removed null sessions, `strapi_session` will just return `None` if a no strapi session exists.
- Strapi.request can now be used outside of flask request contexts (as an unauthenticated request).
- Supports 'app logins' as opposed to 'per session (user)' logins. This allow the app to login and request content from strapi without any user sessions. Use `as_app_session = true` on authenticate and request to be able to issue request even without flask's request context (i.e., outside of a route).

## Installation
Recommend to do this in a virtual environment!

### Latest Version
```bash
pip install git+git://github.com/toranova/flask-strapi.git@master
```
### pypi Release
```bash
pip install flask-strapi
```

## Testing the current build
```bash
runtest.sh
```

## Examples
1. [Basic](examples/basic/__init__.py)
2. [Basic (for Strapi V4)](examples/basicV4/__init__.py)

## TODOs
1. Implement unit-testing
