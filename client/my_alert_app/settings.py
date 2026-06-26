"""
Django's settings for my_alert_app project
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-client-side-8000-testing-dashboard-key'

DEBUG = True

# Client configuration
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Application definition
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'alerts',
    'channels',
    'corsheaders',
]

# MIDDLEWARE
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'my_alert_app.urls'

# DRF Config
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
    'UNAUTHENTICATED_USER': None,
    'UNAUTHENTICATED_TOKEN': None,
    'DEFAULT_AUTHENTICATION_CLASSES': [],
}

# CORS settings - Allow requests from SERVER (port 8001)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8001",
    "http://127.0.0.1:8001",
]
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOW_CREDENTIALS = True

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

WSGI_APPLICATION = 'my_alert_app.wsgi.application'
ASGI_APPLICATION = 'my_alert_app.asgi.application'

# Database - Different database name from SERVER
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'client_db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = []

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / "static",
    BASE_DIR,  # For firebase-messaging-sw.js at root
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Channels configuration
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# Client Configuration - Points to ServerSide for testing
CLIENT_CONFIG = {
    'HOST': '127.0.0.1',
    'PORT': 8000,
    'NAME': 'Performance Testing Dashboard Client',
    'SERVER_URLS': {
        'websocket': 'ws://127.0.0.1:8001/ws/alerts/',
        'longpolling': 'http://127.0.0.1:8001/api/poll/alerts/',
        'push': 'http://127.0.0.1:8001/api/push/',
        'health': 'http://127.0.0.1:8001/api/status/',
    }
}

# Performance Testing URLs - Point to ServerSide for CLIENT→SERVER testing
PERFORMANCE_TEST_URLS = {
    'WEBSOCKET_URL': 'ws://127.0.0.1:8001/ws/alerts/',
    'LONGPOLLING_URL': 'http://127.0.0.1:8001/api/poll/alerts/',
    'FIREBASE_URL': 'http://127.0.0.1:8001/api/push',
    'SERVER_BASE_URL': 'http://127.0.0.1:8001',
}

# Firebase Configuration (for client-side)
FIREBASE_CONFIG = {
    'apiKey': "AIzaSyD1C5ob3B7L2N57vrlC-3siYRMwUgGLL7M",
    'authDomain': "myalertappproject.firebaseapp.com",
    'projectId': "myalertappproject",
    'storageBucket': "myalertappproject.firebasestorage.app",
    'messagingSenderId': "628710969002",
    'appId': "1:628710969002:web:735611410af3e440d5cad3",
    'measurementId': "G-S9HE2VRY8T"
}

# Enhanced Performance Testing Configuration
ENHANCED_PERFORMANCE_CONFIG = {
    'ENABLED': True,
    'MAX_CONCURRENT_TESTS': 20,
    'DEFAULT_TEST_DURATION': 120,
    'MAX_TEST_DURATION': 600,
    'RESOURCE_MONITORING_INTERVAL': 1.0,
    'RESULTS_RETENTION_COUNT': 10,
    'CLIENT_TO_SERVER_TESTING': True,
    'SERVER_ENDPOINTS': {
        'websocket': 'ws://127.0.0.1:8001/ws/alerts/',
        'longpolling': 'http://127.0.0.1:8001/api/poll/alerts/',
        'firebase': 'http://127.0.0.1:8001/api/push/',
        'health': 'http://127.0.0.1:8001/api/status/'
    }
}

# Enhanced Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
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
            'filename': BASE_DIR / 'logs' / 'client.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'alerts': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'alerts.enhanced_performance_views': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

# Create logs directory
os.makedirs(BASE_DIR / 'logs', exist_ok=True)
