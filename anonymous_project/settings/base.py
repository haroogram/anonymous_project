"""
Django base settings for anonymous_project project.

공통 설정을 정의합니다.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_beat',  # Celery Beat 스케줄 관리
    'main',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'main.middleware.VisitorCountMiddleware',  # 접속자 수 추적 미들웨어
]

ROOT_URLCONF = 'anonymous_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'main.context_processors.visitor_stats',
            ],
        },
    },
]

WSGI_APPLICATION = 'anonymous_project.wsgi.application'

# Database 설정은 development.py와 production.py에서 환경 변수로 설정

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators
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
# https://docs.djangoproject.com/en/6.0/topics/i18n/
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/
# 주의: production.py에서 S3를 사용하는 경우 이 값이 덮어써집니다.
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
# https://docs.djangoproject.com/en/6.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Redis Cache 설정 (ElastiCache for Redis 지원)
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)  # ElastiCache의 경우 password 인증 사용 가능
REDIS_DB = int(os.getenv('REDIS_DB', '0'))

# Redis 연결 URL 구성
if REDIS_PASSWORD:
    REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
else:
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,  # 연결 타임아웃 (초)
            'SOCKET_TIMEOUT': 5,  # 소켓 타임아웃 (초)
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            # ElastiCache 사용 시 SSL/TLS 설정 (필요한 경우)
            # 'CONNECTION_POOL_KWARGS': {
            #     'ssl': True,
            #     'ssl_cert_reqs': None,
            # },
        },
        'KEY_PREFIX': 'anonymous_project',
        'TIMEOUT': 300,  # 기본 캐시 타임아웃 (초)
    }
}

# Redis 직접 접근을 위한 설정 (django-redis의 get_redis_connection 사용)
REDIS_CONNECTION_PARAMS = {
    'host': REDIS_HOST,
    'port': REDIS_PORT,
    'db': REDIS_DB,
    'decode_responses': True,
}
if REDIS_PASSWORD:
    REDIS_CONNECTION_PARAMS['password'] = REDIS_PASSWORD

# Celery 설정
CELERY_BROKER_URL = REDIS_URL  # ElastiCache Redis를 브로커로 사용
CELERY_RESULT_BACKEND = REDIS_URL  # 작업 결과 저장소
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE  # 'Asia/Seoul'
CELERY_ENABLE_UTC = False

# Celery Beat 설정 (Redis 기반 분산 락 사용)
# DatabaseScheduler를 사용하면 Django admin에서 스케줄을 관리할 수 있음
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Celery Beat 스케줄 정의 -> DB로 관리
# from celery.schedules import crontab

# CELERY_BEAT_SCHEDULE = {
#     'sync-visitor-stats-daily': {
#         'task': 'main.tasks.sync_visitor_stats_task',
#         'schedule': crontab(hour=0, minute=1),  # 매일 자정 1분에 실행
#         'options': {'expires': 60 * 60},  # 작업 만료 시간 (1시간)
#     },
# }

