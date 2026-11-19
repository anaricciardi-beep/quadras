
"""
Configurações do projeto Django - Quadras Esportivas.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


# DIRETÓRIO PRINCIPAL
BASE_DIR = Path(__file__).resolve().parent.parent

# Carregar variáveis do arquivo .env
load_dotenv(BASE_DIR / ".env")


# CONFIGURAÇÕES DE SEGURANÇA
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

DEBUG = True

ALLOWED_HOSTS = []


# APLICAÇÕES INSTALADAS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',
]


# MIDDLEWARES
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# CONFIGURAÇÃO DAS URLS
ROOT_URLCONF = 'config.urls'


# CONFIGURAÇÃO DOS TEMPLATES HTML
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'DIRS': [
            BASE_DIR / 'app' / 'templates',
        ],

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


# CONFIGURAÇÃO WSGI
WSGI_APPLICATION = 'config.wsgi.application'


# BANCO DE DADOS POSTGRESQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'quadras',
        'USER': 'postgres',
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# VALIDAÇÃO DE SENHAS
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


# IDIOMA E FUSO HORÁRIO
LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# ARQUIVOS ESTÁTICOS - CSS, JS E IMAGENS
STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / 'app' / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'


# TIPO DE CHAVE PRIMÁRIA PADRÃO
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# CONFIGURAÇÃO DE EMAIL PARA DESENVOLVIMENTO
MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}
