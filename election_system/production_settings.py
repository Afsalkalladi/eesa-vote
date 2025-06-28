"""
Production settings for Django Election System.
"""
import os
from .settings import *

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add WhiteNoise for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-9elfa#$5$9hlf0vu112ag)r$3f5q7^zq4-ttoswil+5reak=jb')

# Allowed hosts - will be set by Render
ALLOWED_HOSTS = [
    '.onrender.com',
    'localhost',
    '127.0.0.1',
]

# Add your custom domain when you get one
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Database configuration for production
# Use PostgreSQL exclusively on production
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is required for production. "
        "Please create a PostgreSQL database on Render and set the DATABASE_URL."
    )

# Production: Use PostgreSQL from Render
import dj_database_url
DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL)
}

# Static files configuration for production
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# WhiteNoise configuration for serving static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Configure WhiteNoise to also serve media files in production
# This is a temporary solution - for production, use cloud storage like AWS S3
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True

# Media files configuration for production
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# GitHub storage configuration for free cloud image storage
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', None)
GITHUB_IMAGES_REPO = os.environ.get('GITHUB_IMAGES_REPO', None)  # format: "username/repo-name"
GITHUB_IMAGES_BRANCH = os.environ.get('GITHUB_IMAGES_BRANCH', 'main')
USE_GITHUB_STORAGE = os.environ.get('USE_GITHUB_STORAGE', 'False').lower() == 'true'

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# Ensure media directory exists and has proper permissions
import os
os.makedirs(MEDIA_ROOT, exist_ok=True)

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 86400
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# If you want to use HTTPS (recommended)
if os.environ.get('USE_HTTPS', 'False').lower() == 'true':
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
