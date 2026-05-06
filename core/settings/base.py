"""
Base Django settings for core project.

This file contains shared configuration for all environments.
Environment-specific overrides (local/production) live in:
- core/settings/dev.py
- core/settings/prod.py
"""
from datetime import timedelta
from pathlib import Path

# -------------------------------------------------------------------
# PATHS
# -------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------------------------------
# APPLICATIONS
# -------------------------------------------------------------------

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'drf_spectacular',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_yasg',
]

MY_APPS = [
    'apps.shared',
    'apps.users',
    'apps.locations',
    'apps.orders',
    'apps.shipments',
    'apps.tracking',
    'apps.payments',
    'apps.notifications',
    'apps.reports',
]

INSTALLED_APPS += THIRD_PARTY_APPS
INSTALLED_APPS += MY_APPS

# -------------------------------------------------------------------
# MIDDLEWARE
# -------------------------------------------------------------------

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.shared.middleware.permissions.EndpointPermissionMiddleware',

    # "corsheaders.middleware.CorsMiddleware",
]

# -------------------------------------------------------------------
# URLS / WSGI
# -------------------------------------------------------------------

ROOT_URLCONF = 'core.urls'
WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'

# -------------------------------------------------------------------
# TEMPLATES
# -------------------------------------------------------------------

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR.parent / 'templates'],
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

# -------------------------------------------------------------------
# AUTH / PASSWORDS
# -------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -------------------------------------------------------------------
# INTERNATIONALIZATION
# -------------------------------------------------------------------

LANGUAGE_CODE = 'en'
LANGUAGES = (
    ('en', 'English'),
    ('ru', 'Russian'),
    ('uz', 'Uzbek'),
)

LOCALE_PATHS = (BASE_DIR / 'locale',)

TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

# -------------------------------------------------------------------
# STATIC & MEDIA FILES
# -------------------------------------------------------------------

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR.parent.parent / 'static'
STATICFILES_DIRS = [BASE_DIR.parent / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR.parent.parent / 'media'

# -------------------------------------------------------------------
# DEFAULT PRIMARY KEY TYPE
# -------------------------------------------------------------------

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# -------------------------------------------------------------------
# DJANGO REST FRAMEWORK CONFIG
# -------------------------------------------------------------------

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    # 'DEFAULT_FILTER_BACKENDS': [
    #     'django_filters.rest_framework.DjangoFilterBackend',
    # ],
    'PAGE_SIZE': 20,
    'EXCEPTION_HANDLER': 'apps.shared.exceptions.handler.custom_exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'apps.shared.pagination.StandardPagination',
}

# -------------------------------------------------------------------
# DRF SPECTACULAR CONFIG
# -------------------------------------------------------------------


SPECTACULAR_SETTINGS = {
    'TITLE': 'Green Citizen | Make Your Life Healthier',
    'DESCRIPTION': 'Be the small part of big changes',
    'VERSION': '1.0.0',
}

# -------------------------------------------------------------------
# SIMPLEJWT CONFIG
# -------------------------------------------------------------------


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=10),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# -------------------------------------------------------------------
# CORS CONFIG
# -------------------------------------------------------------------

CORS_ALLOW_ALL_ORIGINS = True  # Dev only — tighten in production

# Swagger settings
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'JWT token qo\'ying: "Bearer <token>"'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
}

# -------------------------------------------------------------------
# JAZZMIN CONFIG
# -------------------------------------------------------------------
JAZZMIN_SETTINGS = {
    "site_title": "Pochta-Service Admin",
    "site_header": "Pochta-Service",
    "site_brand": "Pochta-Service",
    "site_logo": None,
    "welcome_sign": "Welcome to the Pochta-Service Admin Panel",
    "copyright": "Pochta-Service Ltd",
    "search_model": ["users.User", "orders.Order"],
    "user_avatar": None,
    "topmenu_links": [
        {"name": "Home",  "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "View Site", "url": "/", "new_window": True},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "users.User": "fas fa-user",
        "users.UserAddress": "fas fa-map-marker-alt",
        "locations.Region": "fas fa-map",
        "locations.City": "fas fa-city",
        "orders.Order": "fas fa-box",
        "shipments.Shipment": "fas fa-truck",
        "payments.Payment": "fas fa-credit-card",
        "notifications.Notification": "fas fa-bell",
        "tracking.TrackingEvent": "fas fa-route",
        "shared.FAQ": "fas fa-question-circle",
        "shared.Media": "fas fa-image",
        "shared.Onboarding": "fas fa-info-circle",
        "token_blacklist.OutstandingToken": "fas fa-key",
        "token_blacklist.BlacklistedToken": "fas fa-ban",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": False,
    "custom_css": None,
    "custom_js": None,
    "show_ui_builder": True,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": "darkly",
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}