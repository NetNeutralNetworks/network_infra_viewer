import os

basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = "K7MffxWz0gZzyBiIRMqneE9sabXPy8CR"

OAUTH_PROVIDERS = [{
  'name':'authentik',
    'token_key':'access_token',
    'icon':'fa-fingerprint',
        'remote_app': {
            'api_base_url':'https://authentik.c0000.ncubed.io',
            'client_kwargs':{
                'scope': 'email profile'
            },
            'access_token_url':'https://authentik.c0000.ncubed.io/application/o/token/',
            'authorize_url':'https://authentik.c0000.ncubed.io/application/o/authorize/',
            'request_token_url': None,
            'client_id': 'xxx',
            'client_secret': 'xxx',
        }
   },
]


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
AUTH_TYPE = 1
AUTH_ROLE_ADMIN = "Admin"
AUTH_ROLE_PUBLIC = "Public"
# APP_NAME = "My App Name"
# APP_ICON = "static/img/logo.jpg"
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