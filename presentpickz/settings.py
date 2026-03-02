import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-key')
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost 127.0.0.1 .railway.app .up.railway.app').split()
# Add your Namecheap domain here or in Railway Variables
if os.getenv('CUSTOM_DOMAIN'):
    ALLOWED_HOSTS.append(os.getenv('CUSTOM_DOMAIN'))

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'products',
    'orders',
    'users.apps.UsersConfig',
    'cart',
    
    # Allauth
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
ACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_AUTO_SIGNUP = True 
SOCIALACCOUNT_ADAPTER = 'users.adapter.MySocialAccountAdapter'
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True 
SOCIALACCOUNT_QUERY_EMAIL = True

# Authentication settings (Optimized for modern Allauth 65+)
ACCOUNT_PRESERVE_USERNAME_CASING = False
ACCOUNT_SIGNUP_FIELDS = ['email', 'password1', 'password2']
ACCOUNT_LOGIN_METHODS = ['email']
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False  # FIXED: Removed old warnings

# CRITICAL: Disable the signup form completely for direct social login
SOCIALACCOUNT_SIGNUP_FORM_CLASS = None


SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'APP': {
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'secret': os.getenv('GOOGLE_CLIENT_SECRET'),
            'key': ''
        }
    }
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'presentpickz.middleware.RoleBasedAccessMiddleware',  # STRICT AUTH SEPARATION
    'presentpickz.splash_middleware.SplashScreenMiddleware',  # Creative splash on all pages
]

ROOT_URLCONF = 'presentpickz.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'users.context_processors.wishlist_context',
                'users.context_processors.cart_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'presentpickz.wsgi.application'

# Database configuration (Auto-detects Railway's DATABASE_URL)
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
        ssl_require=not DEBUG
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'core' / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# High-Performance Static & Media Files (100% FREE)
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
}

WHITENOISE_MAX_AGE = 31536000

# FIXED: Serve media through WhiteNoise for 100% free high-speed hosting
# This ensures images load even if the server is under load or on a custom domain.
WHITENOISE_ROOT = BASE_DIR / 'media'

# Standard media settings for stability
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Cashfree Settings
CASHFREE_APP_ID = "YOUR_CASHFREE_APP_ID"  # Replace with actual App ID
CASHFREE_SECRET_KEY = "YOUR_CASHFREE_SECRET_KEY"  # Replace with actual Secret Key
CASHFREE_ENV = "TEST"  # or PROD
CASHFREE_API_URL = "https://sandbox.cashfree.com/pg/orders" if CASHFREE_ENV == "TEST" else "https://api.cashfree.com/pg/orders"

# Email Configuration - PRODUCTION MODE (Gmail SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = f'Present Pickz <{os.getenv("EMAIL_HOST_USER")}>'

# CSRF Settings
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000', 
    'http://localhost:8000',
    'https://*.railway.app'
]
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript to read CSRF cookie
CSRF_USE_SESSIONS = False
CSRF_COOKIE_SAMESITE = 'Lax'  # Allow some cross-site usage
CSRF_COOKIE_SECURE = not DEBUG  # Set to True in production with HTTPS
SESSION_COOKIE_SECURE = not DEBUG

# Security Settings for Production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# Jazzmin Settings for Premium Dashboard
JAZZMIN_SETTINGS = {
    "site_title": "Present Pickz Admin",
    "site_header": "Present Pickz",
    "site_brand": "Present Pickz",
    "site_logo": "images/brand_logo.jpg",
    "login_logo": "images/brand_logo.jpg",
    "welcome_sign": "Welcome to Present Pickz Admin",
    "copyright": "Present Pickz Ltd",
    "search_model": ["auth.User", "products.Product"],
    "user_avatar": None,
    "topmenu_links": [
        {"name": "Home", "url": "home", "permissions": ["auth.view_user"]},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "products.Product": "fas fa-gift",
        "products.Category": "fas fa-list",
        "orders.Order": "fas fa-shopping-cart",
        "orders.Refund": "fas fa-undo",
    },
    "order_with_respect_to": ["products", "orders", "auth"],
    "theme": "flatly",
    "dark_mode_theme": "darkly",
}

JAZZMIN_UI_LOGS = {
    "theme": "flatly",
    "dark_mode_theme": "darkly",
}
