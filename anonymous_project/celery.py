"""
Celery 설정 파일
"""
import os
from celery import Celery

# Django 설정 모듈 설정
# 환경 변수가 없으면 기본값으로 development 사용
os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.getenv(
    'DJANGO_SETTINGS_MODULE', 
    'anonymous_project.settings.development'
))

app = Celery('anonymous_project')

# Django 설정에서 Celery 관련 설정을 로드 (CELERY_로 시작하는 설정들)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Django 앱에서 tasks.py 파일을 자동으로 찾아서 등록
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """디버깅용 테스트 태스크"""
    print(f'Request: {self.request!r}')

