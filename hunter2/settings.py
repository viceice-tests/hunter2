from .utils import load_or_create_secret_key
import environ

# Load the current environment profile
root = environ.Path(__file__) - 2
env = environ.Env()

# Default settings which should be overridden by environment variables
DEBUG         = env.bool      ('H2_DEBUG',         default=False)
LOG_LEVEL     = env.str       ('H2_LOG_LEVEL',     default='WARNING')
LANGUAGE_CODE = env.str       ('H2_LANGUAGE_CODE', default='en-gb')
TIME_ZONE     = env.str       ('H2_TIME_ZONE',     default='Europe/London')
ALLOWED_HOSTS = env.list      ('H2_ALLOWED_HOSTS', default=['*'])
INTERNAL_IPS  = env.list      ('H2_INTERNAL_IPS',  default=['127.0.0.1'])
EMAIL_CONFIG  = env.email_url ('H2_EMAIL_URL',     default='smtp://localhost:25')
DATABASES = {
    'default': env.db('H2_DATABASE_URL', default="postgres://postgres:postgres@db:5432/postgres")
}
CACHES = {
    'default': env.cache_url('H2_CACHE_URL', default="dummycache://" )
}

# Generate a secret key and store it the first time it is accessed
SECRET_KEY = load_or_create_secret_key("/config/secrets.ini")

# Load the email configuration
vars().update(EMAIL_CONFIG)

BASE_DIR = root()

# Application definition
TEST_RUNNER = 'hunter2.tests.TestRunner'

ACCOUNT_ACTIVATION_DAYS = 7

ACCOUNT_EMAIL_REQUIRED = True

ACCOUNT_EMAIL_VERIFICATION = 'none'

AUTHENTICATION_BACKENDS = (
    'allauth.account.auth_backends.AuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
    'rules.permissions.ObjectPermissionBackend',
)

DEBUG_TOOLBAR_PATCH_SETTINGS = False

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.openid',
    'debug_toolbar',
    'nested_admin',
    'rules.apps.AutodiscoverRulesConfig',
    'sortedm2m',
    'subdomains',
    'events',
    'teams',
    'hunts',
    'hunter2',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
        },
        'django.db': {
        },
    },
}

LOGIN_REDIRECT_URL = '/'

LOGIN_URL = '/accounts/login/'

MEDIA_ROOT = '/uploads/'

MEDIA_URL = '/media/'

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'subdomains.middleware.SubdomainURLRoutingMiddleware',
    'django.middleware.common.CommonMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'events.middleware.EventMiddleware',
    'teams.middleware.TeamMiddleware',
)

ROOT_URLCONF = 'hunter2.urls'

SOCIALACCOUNT_AUTO_SIGNUP = False

SOCIALACCOUNT_PROVIDERS = {
    'openid': {
        'SERVERS': [{
            'id': 'steam',
            'name': 'Steam',
            'openid_url': 'http://steamcommunity.com/openid',
        }]
    }
}

STATIC_ROOT = '/static/'

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    'hunter2/static',
)

TEMPLATES = [
    {
        'APP_DIRS': True,
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'hunter2/templates',
        ],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.contrib.messages.context_processors.messages',
                'teams.context_processors.event_team',
            ],
        },
    },
]

SECURE_BROWSER_XSS_FILTER = True

SECURE_CONTENT_TYPE_NOSNIFF = True

SITE_ID = 1

SUBDOMAIN_URLCONFS = {
    'admin': 'hunter2.urls.admin',
    'www': 'hunter2.urls.www',
}

USE_I18N = True

USE_L10N = True

USE_TZ = True

WSGI_APPLICATION = 'hunter2.wsgi.application'

X_FRAME_OPTIONS = 'DENY'
