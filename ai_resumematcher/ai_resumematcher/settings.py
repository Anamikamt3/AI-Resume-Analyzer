
import os
import environ
from pathlib import Path
from datetime import timedelta
import mimetypes

# Force Windows to recognize correct CSS and JS types
mimetypes.add_type("text/css", ".css", True)
mimetypes.add_type("application/javascript", ".js", True)

# 1. Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Initialize environment variables engine
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# 3. Security Settings (Pulled dynamically from secure local .env variables)
SECRET_KEY = env('SECRET_KEY', default='django-insecure-fallback-key-for-local-dev')

# FIX: Allow DEBUG to pull from env, but default to True locally so runserver can serve assets!
DEBUG = env.bool('DEBUG', default=True)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])

# 4. Installed Application Modules Register
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-Party Dependencies packages
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_yasg', 
    
    # Local Custom Core application
    'analyzer',
]

# 5. Middleware Chain Configuration
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Handles connecting across origins safely
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # FIX: Moved to the top right after SecurityMiddleware!
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ai_resumematcher.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        #'DIRS': [],
        # 'DIRS': [BASE_DIR / 'templates'], # <-- FIX: Tell Django to look at your root templates folder
        'DIRS': [
            BASE_DIR / 'templates', 
            BASE_DIR.parent / 'templates'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ai_resumematcher.wsgi.application'

# 6. Database Core Integration Configuration
DATABASES = {
    'default': env.db('DATABASE_URL')
}

# 7. Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 8. Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# 9. Cross-Origin Resource Sharing (CORS) Configuration
CORS_ALLOW_ALL_ORIGINS = True 

# 10. Django REST Framework & Simple JWT Engine Configurations
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1), 
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'SIGNING_KEY': SECRET_KEY,
}

# 11. Storage Configurations handling static and asset document uploads
STATIC_URL = '/static/'  # Added forward slash for path uniformity
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATIC_URL = 'static/'

# FIX: Force Django to search your precise root folders using absolute pathing
STATICFILES_DIRS = [
    path for path in [
        os.path.join(BASE_DIR, 'static'),
        os.path.join(BASE_DIR.parent, 'static'),
    ] if os.path.exists(path)
]
'''STATICFILES_DIRS = [
    #os.path.join(BASE_DIR, 'static'),
    #os.path.join(BASE_DIR.parent, 'static'),
    os.path.join(BASE_DIR, 'static'),
]'''
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder', 
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' 

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
}