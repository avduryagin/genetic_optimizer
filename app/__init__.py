import os
import sys
import secrets
from flask import Flask
import logging
from logging import Formatter
from app import providers
from app.flask_config import Config

app_flask = Flask(__name__)
app_flask.config.from_object(Config)
provider=providers.load_from_env()
if provider is None:
    provider=providers.Provider()

app_flask.config['OAUTH2_PROVIDERS'] = dict({})
app_flask.config['OAUTH2_PROVIDERS'][provider.provider_id]=provider
app_flask.config['SECRET_KEY']=app_flask.config['OAUTH2_PROVIDERS'][provider.provider_id].client_id


console=logging.StreamHandler()
formatter=Formatter('%(message)s'
    #'%(asctime)s %(levelname)s: %(message)s '
    #'[in %(pathname)s:%(lineno)d]'
)
console.setFormatter(formatter)
console.setLevel(logging.INFO)
logging.getLogger("").addHandler(console)
logging.root.setLevel("INFO")

from app import routes
#from app import oauth2validation
from app import calculation