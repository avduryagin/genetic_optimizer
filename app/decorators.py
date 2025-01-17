from app import app_flask
@app_flask.after_request
def add_headers(response):
    response.headers['Content-Security-Policy'] = app_flask.config['CSP']
    response.headers['Strict-Transport-Security'] = app_flask.config['HSTS']
    response.headers['X-Permitted-Cross-Domain-Policies'] = app_flask.config['X_PERMITTED_CROSS_DOMAIN_POLICIES']
    response.headers['X-Frame-Options'] = app_flask.config['X_FRAME_OPTIONS']
    response.headers['X-XSS-Protection'] = app_flask.config['X_XSS_PROTECTION']
    response.headers['X-Content-Type-Options'] = app_flask.config['X_CONTENT_TYPE_OPTIONS']
    response.headers['X-Download-Options'] = app_flask.config['X_DOWNLOAD_OPTIONS']
    #response.headers['Expect-CT'] = app_flask.config['EXCEPT_CT']
    return response