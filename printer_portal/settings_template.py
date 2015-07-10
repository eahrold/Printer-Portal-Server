"""
Django settings for printer_portal project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(PROJECT_DIR, ...)
import os
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# CHANGE THIS!!!!
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'zy#z(t$o$rf4ouzslhazo9iywe)fr(udqz59j2k6k#aq-+)x+k'

#######################################################
##  Configure printer_portal server specific items ##
#######################################################
# The title site.
APP_NAME = "Printer Portal"

# Name of your organization used only for branding
ORGANIZATION_NAME = "My Great Orginization"

# Set to true if you want the ability to upload and
# server PPD files and Sparkle update.
# NOTE: you cannot serve files when running via Heroku
SERVE_FILES = False

# Configuring Sparkle Updates
# if set to True you will be able to upload versions of
# Printer Portal.app and it will automatically create AppCasts
# for Sparkle, otherwise it will use the GITHUB_APPCAST_URL.
# NOTE: you cannot host updates when running via Heroku
HOST_SPARKLE_UPDATES = False

# Should access to the printers be available via
# the REST api interface at http(s)://server.com/api
# Currently this is purely experimental.
INCLUDE_REST_API = True

# Set this to True to disable the 'django.views.static.serve'
RUNNING_ON_APACHE = False

# If not hosting sparkle updates, it will use this url for AppCasts.
# If building a custom version of Printer Portal.app to provide a
# print quota software for your environment set this to your forks URL
GITHUB_APPCAST_URL = "https://raw.githubusercontent.com/eahrold/Printer_Portal/master/Downloads/appcast.xml"

# If not hosting sparkle updates, set these to where the latest release can be downloaded.
GITHUB_LATEST_RELEASE = {'user':'eahrold', 'repo':'Printer_Portal'}

# The URL scheme the client app responsd to. It will automatically
# be appended with "s" if the serve is secure (i.e. https)
CLIENT_URL_TYPE = "printerportal"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/
SITE_ID = 1

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

LOGIN_URL = 'django.contrib.auth.views.login'
LOGOUT_URL = 'django.contrib.auth.views.logout'
LOGIN_REDIRECT_URL = 'manage'


''' Static File Settings '''
# Absolute file system path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'files/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/files/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static/')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_DIR, 'site_static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

'''Template Settings'''
TEMPLATE_DEBUG = True

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #'django.template.loaders.eggs.Loader',
)

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, 'templates'),
)

from django.conf import global_settings
TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    'printer_portal.context_processors.update_server',
    'printer_portal.context_processors.app_name',
    'django.contrib.auth.context_processors.auth',
    )


# Application definition. Start it as a list so it
# can be conditionally updated, then convert to a
# tuple for Django.
_CONDITIONAL_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Contrib apps
    'bootstrap_toolkit',

    # Project level apps
    'printers',
]

if HOST_SPARKLE_UPDATES:
    _CONDITIONAL_APPS.append('sparkle')

if INCLUDE_REST_API:
    _CONDITIONAL_APPS.append('rest_framework')

INSTALLED_APPS = tuple(_CONDITIONAL_APPS)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'printer_portal.urls'

WSGI_APPLICATION = 'printer_portal.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

## Settings For deploying to heroku
if 'DYNO' in os.environ:
    print "Deployed to Heroku."
    # Parse database configuration from $DATABASE_URL
    import dj_database_url
    DATABASES['default'] =  dj_database_url.config()

    # Honor the 'X-Forwarded-Proto' header for request.is_secure()
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # Allow all host headers
    ALLOWED_HOSTS = ['*']

    # Make Sure Debugging is false to Heroku
    DEBUG=False
    # If serving from heroku disable the ability to server files
    HOST_SPARKLE_UPDATES = False
    SERVE_FILES=False
elif 'DB_ENV_PGDATA' in os.environ:
    print "Using postgresql_psycopg2"
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'postgres',
            'USER': 'postgres',
            'HOST': 'db',
            'PORT': 5432,
            }
        }
else:
    print "Using default sqlite3 db"
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(PROJECT_DIR, 'printer_portal.db'),
        }
    }


TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True
