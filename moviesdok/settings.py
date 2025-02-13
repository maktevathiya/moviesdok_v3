import os
from pathlib import Path
import environ
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment variables
env = environ.Env()

# Read the .env file (make sure it's in the root directory)
env.read_env(BASE_DIR / ".env")

# Use the SECRET_KEY from the .env file
SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
TMDB_API_KEY = env("TMDB_API_KEY")

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.ngrok-free.app']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Django apps
    'django.contrib.sites',      # Required for Django-Allauth

    # Allauth apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    
    # Social account providers (optional, add based on need)
    # 'allauth.socialaccount.providers.google',  # Example: for Google OAuth
    # 'allauth.socialaccount.providers.facebook',

    #apps
    'homepage',
    'detail_page',  
    'watchlist',
    'user_history',
    'second_level_pages',
    'links',
    'telegram_bot',

    #css
    'tailwind',
    'theme',  # name this as your theme app (you can use any name)
    'django_browser_reload'

]

#for the tailwind css
TAILWIND_APP_NAME = 'theme'
INTERNAL_IPS = [
    "127.0.0.1",
]
NPM_BIN_PATH = r"C:\Program Files\nodejs\npm.cmd"  # Use raw string to handle backslashes



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #allauth middleware
    'allauth.account.middleware.AccountMiddleware',
    #tailwind reloader
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

ROOT_URLCONF = 'moviesdok.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'moviesdok.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'theme/static')]


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


#extra code from the default
SITE_ID = 1  # Required for Django-Allauth

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',      # Default backend
    'allauth.account.auth_backends.AuthenticationBackend',  # Allauth backend
]

ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = "optional"  # Options: "none", "optional", "mandatory"
ACCOUNT_USERNAME_REQUIRED = True
LOGIN_REDIRECT_URL = '/'  # Redirect after login
LOGOUT_REDIRECT_URL = '/' # Redirect after logout
ACCOUNT_EMAIL_SUBJECT_PREFIX = '[Your Site] '

# Email backend configuration for password reset
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Change to SMTP for production
DEFAULT_FROM_EMAIL = 'webmaster@localhost'


STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') #for production for the command 'python manage.py collectstatic'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',  # Use FileBasedCache for development
        'LOCATION': r'C:\Users\SHIVA\website\moviesdok_v3\moviesdok\cache',  # Set the cache directory
        'TIMEOUT': 21600,  # Cache timeout in seconds (6 hours)
    }
}
