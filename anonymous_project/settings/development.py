"""
Django development settings for anonymous_project project.

개발 환경 설정입니다.
"""

from .base import *
# base.py에서 이미 env를 초기화했으므로 재사용

# SECURITY WARNING: keep the secret key used in production secret!
# 개발 환경에서는 .env 파일에서 가져오거나 기본값 사용
SECRET_KEY = env('SECRET_KEY', default='django-insecure-dev-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', default=True)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# Database 설정 - MariaDB
# 환경 변수가 없으면 SQLite를 기본값으로 사용 (로컬 개발 편의성)
DB_ENGINE = env('DB_ENGINE', default='sqlite3')
if DB_ENGINE == 'mysql':
    import pymysql
    pymysql.install_as_MySQLdb()
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': env('DB_NAME', default='anonymous_db'),
            'USER': env('DB_USER', default='root'),
            'PASSWORD': env('DB_PASSWORD', default=''),
            'HOST': env('DB_HOST', default='localhost'),
            'PORT': env('DB_PORT', default=3306),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
else:
    # SQLite (기본값 - 환경 변수 없을 때)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
