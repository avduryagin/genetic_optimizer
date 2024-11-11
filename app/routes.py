from app import app_flask

@app_flask.route('/')
@app_flask.route('/index')
def index():
    return "OIS.PyServices"

@app_flask.route('/health/live')
def health():
    return 'live'