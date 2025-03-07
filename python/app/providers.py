import os
import requests
from urllib.parse import urljoin

class Providers:
    def __init__(self):
        self._providers=dict({})

class Provider:
    def __init__(self,provider_id="OIS-HUB",client_id="ois-pipe-calccrashpipe",client_secret="678b4e93-0798-4ea1-ace6-f8622869fd91",audience=None,
                 scope="openid",authorization_endpoint="https://ois-hub.okd.asuproject.ru/oauth2/authorize",
                 token_endpoint= "https://ois-hub.okd.asuproject.ru/oauth2/token",redirect_uri="https://ois-pipe-calccrashpipe-gpn-pipe-dev.okd.asuproject.ru/callback",
                 jwks_uri="https://ois-hub.okd.asuproject.ru/oauth2/jwks"):
        self.provider_id=provider_id
        self.client_id=client_id
        self.client_secret=client_secret
        self.audience = self.client_id
        if audience is not None:
            self.audience=audience
        self.scope=scope
        self.authorization_endpoint=authorization_endpoint
        self.token_endpoint=token_endpoint
        self.redirect_uri=redirect_uri
        self.jwks_uri=jwks_uri
        #self.audience='ois-pipe-calccrashpipe'

def load_from_env():
    try:
        tag='.well-known/openid-configuration'
        client_id=os.environ.get('Security__OpenIdConnect__ClientId')
        client_secret=os.environ.get('Security__OpenIdConnect__ClientSecret')
        audience=os.environ.get('Security__OpenIdConnect__Audience')
        redirect_uri=""
        authority_connect=os.environ.get('Security__OpenIdConnect__Authority')
        if authority_connect is not None:
            #discovery=urljoin(authority_connect,tag)
            discovery = urljoin(authority_connect, tag)
            well_known=requests.get(discovery).json()
            authorization_endpoint=well_known['authorization_endpoint']
            token_endpoint=well_known['token_endpoint']
            jwks_uri=well_known['jwks_uri']
            provider=Provider(provider_id=authority_connect,client_id=client_id,client_secret=client_secret,audience=audience,redirect_uri=redirect_uri,authorization_endpoint=authorization_endpoint,
                              token_endpoint=token_endpoint,jwks_uri=jwks_uri)
            return provider
        return None
    except Exception:
        return None




