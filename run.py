import os
from app import app
from dotenv import load_dotenv

load_dotenv()

WEBSERVER_LISTEN_IP = os.environ['WEBSERVER_LISTEN_IP']
WEBSERVER_PORT = int(os.environ['WEBSERVER_PORT'])
DEBUG_MODE = os.environ['DEBUG_MODE']

# jaspers proxy super fix
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1)

app.run(host=WEBSERVER_LISTEN_IP, port=WEBSERVER_PORT, debug=DEBUG_MODE)
