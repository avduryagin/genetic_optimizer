from app import app_flask
from flask import request
from app.oauth2validation import jwt_token

@app_flask.route('/')
@app_flask.route('/index')
def index():
    return "OIS.PyServices"

@app_flask.route('/health/live')
def health():
    return 'live'

@app_flask.route('/token')
def token():
    return jwt_token(request)