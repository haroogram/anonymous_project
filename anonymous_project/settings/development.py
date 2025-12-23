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
