"""
WSGI config for anonymous_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

from django.core.wsgi import get_wsgi_application

# 기본값은 개발 환경, 배포 시에는 서버에서 DJANGO_SETTINGS_MODULE을 직접 설정
# 예: export DJANGO_SETTINGS_MODULE=anonymous_project.settings.production
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anonymous_project.settings.development')

application = get_wsgi_application()
