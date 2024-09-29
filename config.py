import os
from dotenv import load_dotenv

load_dotenv()

from flask_appbuilder.security.manager import (
    AUTH_OAUTH,AUTH_DB
)

basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = os.environ['APP_SECRET_KEY']

KEYCLOAK_CLIENT_ID = os.environ.get('KEYCLOAK_CLIENT_ID')
KEYCLOAK_CLIENT_SECRET = os.environ.get('KEYCLOAK_CLIENT_SECRET')
KEYCLOAK_DOMAIN = os.environ.get('KEYCLOAK_DOMAIN')

AUTHENTIK_CLIENT_ID = os.environ.get('AUTHENTIK_CLIENT_ID')
AUTHENTIK_CLIENT_SECRET = os.environ.get('AUTHENTIK_CLIENT_SECRET')
AUTHENTIK_DOMAIN = os.environ.get('AUTHENTIK_DOMAIN')

#OAUTH_PROVIDERS = [{
#  'name':'authentik',
#    'token_key':'access_token',
#    'icon':'fa-fingerprint',
#        'remote_app': {
#            'api_base_url':'https://authentik.c0000.ncubed.io',
#            'client_kwargs':{
#                'scope': 'email profile'
#            },
#            'access_token_url':'https://authentik.c0000.ncubed.io/application/o/token/',
#            'authorize_url':'https://authentik.c0000.ncubed.io/application/o/authorize/',
#            'request_token_url': None,
#            'client_id': 'xxx',
#            'client_secret': 'xxx',
#        }
#   },
#]


SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join("/var/lib/appbuilder/data", "app.db")
# SQLALCHEMY_DATABASE_URI = 'mysql://myapp@localhost/myapp'
# SQLALCHEMY_DATABASE_URI = 'postgresql://root:password@localhost/myapp'
BABEL_DEFAULT_LOCALE = "en"


# ------------------------------
# GLOBALS FOR APP Builder
# ------------------------------
FAB_API_SWAGGER_UI = True

BABEL_DEFAULT_LOCALE = "en"
BABEL_DEFAULT_FOLDER = "translations"
LANGUAGES = {
    "en": {"flag": "gb", "name": "English"},
    "pt": {"flag": "pt", "name": "Portuguese"},
    "es": {"flag": "es", "name": "Spanish"},
    "de": {"flag": "de", "name": "German"},
    "zh": {"flag": "cn", "name": "Chinese"},
    "ru": {"flag": "ru", "name": "Russian"},
}

UPLOAD_FOLDER = basedir + "/app/static/uploads/"
IMG_UPLOAD_FOLDER = basedir + "/app/static/uploads/"
IMG_UPLOAD_URL = "/static/uploads/"
#AUTH_TYPE = 1
#AUTH_ROLE_ADMIN = "Admin"
#AUTH_ROLE_PUBLIC = "Public"
APP_NAME = "NIVR"
APP_ICON = "/static/img/ncubed-large.png"
APP_THEME = ""  # default
# APP_THEME = "cerulean.css"
# APP_THEME = "amelia.css"
# APP_THEME = "cosmo.css"
# APP_THEME = "cyborg.css"
# APP_THEME = "flatly.css"
# APP_THEME = "journal.css"
# APP_THEME = "readable.css"
# APP_THEME = "simplex.css"
# APP_THEME = "slate.css"
# APP_THEME = "spacelab.css"
# APP_THEME = "united.css"
# APP_THEME = "yeti.css"

##################################################
# Authentication
##################################################
# The authentication type
# AUTH_OID : Is for OpenID
# AUTH_DB : Is for database
# AUTH_LDAP : Is for LDAP
# AUTH_REMOTE_USER : Is for using REMOTE_USER from web server
# AUTH_OAUTH : Is for OAuth
AUTH_TYPE = AUTH_DB

# Uncomment to setup Full admin role name
AUTH_ROLE_ADMIN = 'nc-fabdv-admin'

# Uncomment and set to desired role to enable access without authentication
AUTH_ROLE_PUBLIC = 'nc-fabdv-viewer'

# Will allow user self registration
AUTH_USER_REGISTRATION = True

# The recaptcha it's automatically enabled for user self registration is active and the keys are necessary
# RECAPTCHA_PRIVATE_KEY = PRIVATE_KEY
# RECAPTCHA_PUBLIC_KEY = PUBLIC_KEY

# Config for Flask-Mail necessary for user self registration
# MAIL_SERVER = 'smtp.gmail.com'
# MAIL_USE_TLS = True
# MAIL_USERNAME = 'yourappemail@gmail.com'
# MAIL_PASSWORD = 'passwordformail'
# MAIL_DEFAULT_SENDER = 'sender@gmail.com'

# The default user self registration role
AUTH_USER_REGISTRATION_ROLE = "nc-fabdv-admin"

# When using OAuth Auth, uncomment to setup provider(s) info
# Google OAuth example:

OAUTH_PROVIDERS = [{
  'name':'authentik',
    'token_key':'access_token',
    'icon':'fa-fingerprint',
        'remote_app': {
            'api_base_url':f'{AUTHENTIK_DOMAIN}',
            'client_kwargs':{
                'scope': 'email profile'
            },
            'access_token_url':f'{AUTHENTIK_DOMAIN}/application/o/token/',
            'authorize_url':f'{AUTHENTIK_DOMAIN}/application/o/authorize/',
            'request_token_url': None,
            'client_id': f'{AUTHENTIK_CLIENT_ID}',
            'client_secret': f'{AUTHENTIK_CLIENT_SECRET}',
        }
   },
       {
        "name": "keycloak",
        "icon": "fa-key",
        "token_key": "access_token",
        "remote_app": {
            "client_id": KEYCLOAK_CLIENT_ID,
            "client_secret": KEYCLOAK_CLIENT_SECRET,
            "api_base_url": f"{KEYCLOAK_DOMAIN}/realms/master/protocol/openid-connect",
            "client_kwargs": {
                "scope": "email profile",
                "verify": False
            },
            "access_token_url": f"{KEYCLOAK_DOMAIN}/realms/master/protocol/openid-connect/token",
            "authorize_url": f"{KEYCLOAK_DOMAIN}/realms/master/protocol/openid-connect/auth",
            "request_token_url": None,
        },
    },
]
