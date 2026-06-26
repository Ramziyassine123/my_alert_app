"""
Django settings for ServerSide project
Port: 8001 (Server)
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-server-side-8001-performance-testing-key'

# ASGI Configuration for WebSocket support
ASGI_APPLICATION = 'ServerSide.asgi.application'

DEBUG = True

# Updated ALLOWED_HOSTS for proper server configuration
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '192.168.1.100']

# Application definition
INSTALLED_APPS = [
    'daphne',  # For WebSocket support - must be first
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'channels',
    'longpolling',
    'push',
    'websocket_alerts',
]

# MIDDLEWARE - Order matters for CORS
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ServerSide.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ServerSide.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'serverside_db.sqlite3',  # Different DB name
    }
}

# Password validation - removed since no authentication
AUTH_PASSWORD_VALIDATORS = []

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files configuration
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS settings - Allow requests from client (port 8000)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Only in development
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Channels configuration for WebSocket
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# Firebase configuration
FIREBASE_SERVICE_ACCOUNT_KEY = BASE_DIR / 'myalertappproject-firebase-adminsdk-fbsvc-4820c32a22.json'

# Alerts JSON file path
ALERTS_JSON_FILE = BASE_DIR / 'alerts.JSON'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'UNAUTHENTICATED_USER': lambda: None,
    'UNAUTHENTICATED_TOKEN': None,
}

# Server Configuration
SERVER_CONFIG = {
    'HOST': '127.0.0.1',
    'PORT': 8001,
    'NAME': 'ServerSide Performance Testing Server',
    'WEBSOCKET_URL': 'ws://127.0.0.1:8001/ws/alerts/',
    'HTTP_BASE_URL': 'http://127.0.0.1:8001',
    'API_ENDPOINTS': {
        'websocket': 'ws://127.0.0.1:8001/ws/alerts/',
        'longpolling': 'http://127.0.0.1:8001/api/poll/alerts/',
        'push': 'http://127.0.0.1:8001/api/push/',
        'health': 'http://127.0.0.1:8001/api/status/',
    }
}

# Performance Testing Configuration
PERFORMANCE_TESTING = {
    'ENABLED': True,
    'MAX_CONCURRENT_CONNECTIONS': 1000,
    'WEBSOCKET_TIMEOUT': 30,
    'LONG_POLLING_TIMEOUT': 30,
    'ALERTS_FILE': 'alerts.JSON',
    'CLIENT_URL': 'http://127.0.0.1:8000',  # Client application URL
}

# Enhanced Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'serverside.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'websocket_alerts': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'longpolling': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'push': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.channels': {
            'handlers': ['file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

# Create logs directory if it doesn't exist
os.makedirs(BASE_DIR / 'logs', exist_ok=True)
