"""
Django 프로젝트 초기화 파일
Celery 앱을 여기서 로드하여 Django 시작 시 Celery가 초기화되도록 함
"""
from .celery import app as celery_app

__all__ = ('celery_app',)

