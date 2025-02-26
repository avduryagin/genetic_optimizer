from jwt import InvalidSignatureError, ExpiredSignatureError
from jwt import PyJWKClient
import os
from app import app_flask
from flask import redirect,abort,request,url_for,flash,session, jsonify
from urllib.parse import urlencode
import requests
import secrets
import functools
import jwt
from app import providers
#@app_flask.route("/authorize")
def oauth2_authorize(provider="OIS-HUB"):
    provider_data = app_flask.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)

    skey=secrets.token_urlsafe(16)
    session['oauth2_state'] = skey

    # create a query string with all the OAuth2 parameters
    qs = urlencode({
        'client_id': provider_data.client_id,
        'redirect_uri':url_for('oauth2_callback',_external=True),
        'response_type': 'code',
        'scope':provider_data.scope,
        'state': session['oauth2_state']})

    # redirect the user to the OAuth2 provider authorization URL
    #return provider_data.authorization_endpoint + '?' + qs
    return redirect(provider_data.authorization_endpoint + '?' + qs)

#@app_flask.route("/callback")
def oauth2_callback(provider="OIS-HUB"):

    provider_data = app_flask.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)

    # if there was an authentication error, flash the error messages and exit
    if 'error' in request.args:
        for k, v in request.args.items():
            if k.startswith('error'):
                flash(f'{k}: {v}')
        return redirect(url_for('index'))

    # make sure that the state parameter matches the one we created in the
    # authorization request
    if request.args['state'] != session.get('oauth2_state'):
        #print("request state {0}, session state {1}".format(request.args['state'],session.get('oauth2_state')))
        abort(401)

    # make sure that the authorization code is present
    if 'code' not in request.args:
        #print("have not found a code")
        abort(401)

    # exchange the authorization code for an access token
    response = requests.post(provider_data.token_endpoint, data={
        'client_id': provider_data.client_id,
        'client_secret': provider_data.client_secret,
        'code': request.args['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': url_for('oauth2_callback', _external=True),
    }, headers={'Accept': 'application/json'})
    if response.status_code != 200:
        abort(401)
    oauth2_token = response.json().get('access_token')
    if not oauth2_token:
        abort(401)
    return response.json()

#@app_flask.route("/refresh")
def oauth2_refresh(provider="OIS-HUB"):
    provider_data = app_flask.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)

    # if there was an authentication error, flash the error messages and exit
    if 'error' in request.args:
        for k, v in request.args.items():
            if k.startswith('error'):
                flash(f'{k}: {v}')
        return redirect(url_for('index'))

    refresh_token=request.headers['Authorization']
    # exchange the authorization code for an access token
    response = requests.post(provider_data.token_endpoint, data={
        'client_id': provider_data.client_id,
        'client_secret': provider_data.client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
    }, headers={'Accept': 'application/json'})
    if response.status_code != 200:
        abort(401)
    oauth2_token = response.json().get('access_token')
    if not oauth2_token:
        abort(401)
    return response.json()



@app_flask.route("/jwks")
def jwks(provider="OIS-HUB"):
    isvalid,msg=jwt_token(request)
    if isvalid:
        return {"user": msg}
    else:
        return abort(401,description=msg)


def jwt_token(request):
    token=None
    user=None
    provider_id=os.environ.get('Security__OpenIdConnect__Authority')
    provider = load_provider(provider_id)
    if provider is None:
        abort(401)
    try:
        bearer=request.headers['Authorization']
        token=bearer.split()[1]
        if token is None:
            raise KeyError
        options={"verify_exp": True,"verify_aud":True}
        optional_custom_headers = {"User-agent": "custom-user-agent"}
        jwks_client = PyJWKClient(provider.jwks_uri, headers=optional_custom_headers)
        signing_key=jwks_client.get_signing_key_from_jwt(token)
        audience=provider.audience
        try:
            decoded = jwt.decode(token, signing_key, algorithms=["RS256"], options=options,audience=audience)
            user=decoded
            return True,user
        except InvalidSignatureError:
            raise KeyError("InvalidSignature")
        except ExpiredSignatureError:
            raise KeyError("ExpiredSignature")

    except KeyError as err:
        return False,err.args[0]
    except Exception as exc_:
        return False, exc_.args[0]



def load_provider(provider_id):
    try:
        provider=app_flask.config['OAUTH2_PROVIDERS'][provider_id]
    except KeyError:
        provider=providers.load_from_env()
    return provider






