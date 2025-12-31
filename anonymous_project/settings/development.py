"""
Django development settings for anonymous_project project.

개발 환경 설정입니다.
"""

from .base import *
import os

# SECURITY WARNING: keep the secret key used in production secret!
# 개발 환경에서는 .env 파일에서 가져오거나 기본값 사용
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Database 설정 - MariaDB
# 환경 변수가 없으면 SQLite를 기본값으로 사용 (로컬 개발 편의성)
DB_ENGINE = os.getenv('DB_ENGINE', 'sqlite3')
if DB_ENGINE == 'mysql':
    import pymysql
    pymysql.install_as_MySQLdb()
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DB_NAME', 'anonymous_db'),
            'USER': os.getenv('DB_USER', 'root'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '3306'),
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
