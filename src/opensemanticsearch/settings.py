"""
Django settings for opensemanticsearch project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add to python path so includes of ETL modules will work in Django environment
import sys
sys.path.append("/usr/lib/python3/dist-packages")
sys.path.append("/usr/lib/python3/dist-packages/opensemanticetl")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^8nhh!o3&s91t33ol^*g_6s=)@)3^s-k=w@u1(5h@83w*hyl0^'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'setup',
    'thesaurus',
    'crawler',
    'files',
    'datasources',
    'annotate',
    'search_list',
    'csv_manager',
    'rss_manager',
    'ontologies',
    'querytagger',
    'morphology',
    'hypothesis',
    'twitter',
    'search_entity',
    'visual_graph_explorer',
    'entity_rest_api',
    'import_export',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'opensemanticsearch.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'opensemanticsearch.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

if os.path.isfile('/etc/opensemanticsearch-django-webapps/my.cnf'):
	
	DATABASES = {
		'default': {
					'ENGINE': 'django.db.backends.mysql',
					'OPTIONS': {
							'read_default_file': '/etc/opensemanticsearch-django-webapps/my.cnf',
					},
				}
	}

else:

	DATABASES = {
	    'default': {
	        'ENGINE': 'django.db.backends.sqlite3',
	        'NAME': '/var/opensemanticsearch/db/db.sqlite3',
	    }
	}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'
#LANGUAGE_CODE = 'de-de'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/var/lib/opensemanticsearch/static/'

MEDIA_ROOT = '/var/opensemanticsearch/media/'
