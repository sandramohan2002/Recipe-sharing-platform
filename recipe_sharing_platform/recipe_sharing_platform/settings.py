"""
Django settings for recipe_sharing_platform project.

Generated by 'django-admin startproject' using Django 3.2.25.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os
import pymysql
pymysql.install_as_MySQLdb()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-&t6ep%lw-^ndhggffo90=ouq&v2_0e^!4d#*l^(9orpy29n^p('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '91fa-117-206-201-197.ngrok-free.app']
#name changed to localhost 


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'recipe',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Required for allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google', 
    'social_django',
    'razorpay',
    #'allauth.socialaccount.providers.github',
    #'allauth.socialaccount.providers.facebook',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'recipe.middleware.CustomAuthMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',

    
]

ROOT_URLCONF = 'recipe_sharing_platform.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                #'recipe_sharing_platform.context_processors.backends',
                
            ],
        },
    },
]

WSGI_APPLICATION = 'recipe_sharing_platform.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
         'ENGINE': 'django.db.backends.mysql',
         'NAME': 'flavornaut',
         'USER': 'root',
         'PASSWORD': '',
         'HOST': 'localhost',  # Or your MySQL server address
         'PORT': '3306',  # Default MySQL port
     }
 }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'Flavoraut_authorcase',
#         'USER': 'Flavoraut_authorcase',
#         'PASSWORD': '04456732859c9ee237e51d854ef093d91235e0f3',
#         'HOST': 'oqil1.h.filess.io', 
#         'PORT': '3307',  
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SITE_ID = 1
# LOGIN_REDIRECT_URL = 'homepage'

# #social app custom settings
# SOCIALACCOUNT_PROVIDERS = {
#     'google': {
#         'SCOPE': ['profile', 'email'],
#         'AUTH_PARAMS': {'access_type': 'online'},
#         'APP': {
#             

LOGIN_URL = 'homepage'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = '/'
# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

#MEDIA_URL = '/media/'
#MEDIA_ROOT=os.path.join(BASE_DIR, 'media/')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['email', 'profile']  # Scopes to request from Google
SOCIAL_AUTH_GOOGLE_OAUTH2_USE_UNIQUE_USER_ID = True  # Use unique user IDs for social auth

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI = 'http://127.0.0.1:8000/complete/google/'

# Email settings (configure as per your email provider)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Use your SMTP host
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'sandramohan2025@mca.ajce.in'  # Replace with your email
EMAIL_HOST_PASSWORD = 'Zoom#2023'  # Replace with your email password
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SUPPORT_EMAIL = 'karthikasandra123@gmail.com'


GEMINI_API_KEY = 'AIzaSyAysIRQcjCirxJpy0UAk9GllCLSO2kQ684'  # Your actual API key
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        '': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Razorpay Settings
RAZORPAY_KEY_ID = 'rzp_test_EYA3vypm9ZHRuN'  # Replace with your actual key
RAZORPAY_KEY_SECRET = 'WTszVCcZyUijmNTdZH1kwWkw'  # Replace with your actual secret
RAZORPAY_CURRENCY = 'INR'

CSRF_TRUSTED_ORIGINS = ['https://91fa-117-206-201-197.ngrok-free.app']
