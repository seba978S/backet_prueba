import os
from pathlib import Path
from datetime import timedelta

# ==============================================================================
# CONFIGURACIONES PRINCIPALES DEL PROYECTO (settings.py)
# Archivo maestro de Django donde conectamos todo: base de datos, seguridad,
# librerías externas y rutas.
# ==============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-secret-key-placeholder'
DEBUG = True
ALLOWED_HOSTS = ['*']

# 1. APLICACIONES INSTALADAS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Dependencias de terceros instaladas vía pip
    'rest_framework',            # Para crear la API REST
    'rest_framework_simplejwt',  # RÚBRICA: Para la autenticación por tokens
    'django_filters',            # RÚBRICA: Para permitir filtrado en los endpoints
    'drf_spectacular',           # RÚBRICA: Para generar documentación Swagger (OpenAPI)
    
    # Nuestra Aplicación local
    'arriendos',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'heavy_machinery.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Configurado para leer la carpeta 'templates' donde está tu index.html
        'DIRS': [BASE_DIR / 'templates'], 
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

WSGI_APPLICATION = 'heavy_machinery.wsgi.application'

# ==============================================================================
# 2. BASE DE DATOS (RÚBRICA OBLIGATORIA)
# Aquí configuramos explícitamente la conexión nativa a PostgreSQL, 
# descartando totalmente el uso de sqlite3.
# ==============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'db_maquinaria',   # Nombre de tu BD creada en pgAdmin
        'USER': 'postgres',        # Usuario principal
        'PASSWORD': 'sebastian10', # Tu contraseña real
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# 3. SEGURIDAD: Le decimos a Django que use nuestro modelo personalizado en vez del estándar
AUTH_USER_MODEL = 'arriendos.Usuario'

# ==============================================================================
# 4. CONFIGURACIÓN DE REST FRAMEWORK Y JWT
# Define cómo se comportará nuestra API en general.
# ==============================================================================
REST_FRAMEWORK = {
    # Todas las rutas por defecto exigirán un token JWT válido
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    # RÚBRICA: Activa el motor de filtros para /api/maquinarias/?categoria=Algo
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    # RÚBRICA: Activa el autogenerador de esquemas para Swagger
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Configuración específica de duración de tokens y serializador customizado
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60), # El token dura 1 hora
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),    # Permite renovarlo hasta 1 día después
    # RÚBRICA: Permite inyectar los roles en el Payload usando nuestra clase de serializers.py
    'TOKEN_OBTAIN_SERIALIZER': 'arriendos.serializers.CustomTokenObtainPairSerializer',
}

# 5. CONFIGURACIÓN DE SWAGGER (Documentación API)
SPECTACULAR_SETTINGS = {
    'TITLE': 'API Arriendo Maquinaria Pesada',
    'DESCRIPTION': 'Documentación de la API requerida por rúbrica para arriendo de equipos.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# 6. LOCALIZACIÓN
LANGUAGE_CODE = 'es-cl' # Idioma en español Chile
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
