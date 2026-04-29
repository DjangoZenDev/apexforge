"""
ApexForge Free Edition — Settings
Django 5.x — Community / Free version
"""
import os
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(DEBUG=(bool, True), LANGUAGE_CODE=(str, "en"), TIME_ZONE=(str, "UTC"))
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="dev-secret-key-change-me-in-production-now-please")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

DJANGO_APPS = [
    "django.contrib.admin","django.contrib.auth","django.contrib.contenttypes",
    "django.contrib.sessions","django.contrib.messages","django.contrib.staticfiles",
    "django.contrib.humanize",
]
THIRD_PARTY_APPS = [
    "django_htmx","widget_tweaks","django_cleanup.apps.CleanupConfig",
    "django_extensions","django_filters","django_q",
]
LOCAL_APPS = [
    "core.apps.CoreConfig","accounts.apps.AccountsConfig",
    "teams.apps.TeamsConfig","players.apps.PlayersConfig",
    "events.apps.EventsConfig","scouting.apps.ScoutingConfig",
    "finance.apps.FinanceConfig","marketing.apps.MarketingConfig",
    "medical.apps.MedicalConfig","tournaments.apps.TournamentsConfig",
    "inventory.apps.InventoryConfig","contracts.apps.ContractsConfig",
    "videos.apps.VideosConfig","staff.apps.StaffConfig",
    "academy.apps.AcademyConfig","organizations.apps.OrganizationsConfig",
    "insights.apps.InsightsConfig",
    # fans not included in free edition
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "core.middleware.ClubContextMiddleware",
    "core.middleware.ActivityLogMiddleware",
    "core.middleware.FreeVersionMiddleware",
]

ROOT_URLCONF = "apexforge.urls"
TEMPLATES = [{"BACKEND":"django.template.backends.django.DjangoTemplates","DIRS":[BASE_DIR/"templates"],"APP_DIRS":True,"OPTIONS":{"context_processors":["django.template.context_processors.debug","django.template.context_processors.request","django.contrib.auth.context_processors.auth","django.contrib.messages.context_processors.messages","django.template.context_processors.i18n","core.context_processors.global_context"]}}]
WSGI_APPLICATION = "apexforge.wsgi.application"
DATABASES = {"default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")}
DATABASES["default"]["ATOMIC_REQUESTS"] = True
AUTH_USER_MODEL = "accounts.User"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME":"django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME":"django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME":"django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME":"django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "core:dashboard"
LOGOUT_REDIRECT_URL = "accounts:login"

LANGUAGE_CODE = env("LANGUAGE_CODE")
LANGUAGES = [("en","English"),("nl","Nederlands"),("de","Deutsch"),("fr","Francais"),("es","Espanol"),("it","Italiano")]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = env("TIME_ZONE")
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="ApexForge <noreply@apexforge.com>")

FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

from django.contrib.messages import constants as messages
MESSAGE_TAGS = {messages.DEBUG:"debug",messages.INFO:"info",messages.SUCCESS:"success",messages.WARNING:"warning",messages.ERROR:"error"}
PAGE_SIZE = 20

Q_CLUSTER = {"name":"apexforge","workers":2,"timeout":90,"retry":120,"queue_limit":50,"bulk":10,"orm":"default","catch_up":False}

STRIPE_PUBLIC_KEY     = env("STRIPE_PUBLIC_KEY",     default="pk_test_placeholder")
STRIPE_SECRET_KEY     = env("STRIPE_SECRET_KEY",     default="sk_test_placeholder")
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET", default="whsec_placeholder")
STRIPE_CURRENCY       = env("STRIPE_CURRENCY",       default="eur")

APEXFORGE_VERSION = "1.0.0"
APEXFORGE_EDITION = "free"
APEXFORGE_SPORT_CHOICES = [
    ("football","Football"),("basketball","Basketball"),("tennis","Tennis"),
    ("rugby","Rugby"),("baseball","Baseball"),("volleyball","Volleyball"),
    ("hockey","Hockey"),("swimming","Swimming"),("athletics","Athletics"),
    ("cycling","Cycling"),("other","Other"),
]
FREE_EDITION_LOCKED_NAMESPACES = frozenset([
    "events","scouting","finance","marketing","medical","contracts",
    "staff","tournaments","academy","inventory","videos","insights","organizations",
])
