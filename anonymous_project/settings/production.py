"""
Django production settings for anonymous_project project.

배포 환경 설정입니다.
EC2 Ubuntu 서버에서 사용합니다.
"""

from .base import *
# base.py에서 이미 env를 초기화했으므로 재사용

# SECURITY WARNING: keep the secret key used in production secret!
# 프로덕션에서는 반드시 환경 변수로 SECRET_KEY를 설정해야 합니다
SECRET_KEY = env('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY 환경 변수가 설정되지 않았습니다!")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', default=False)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])
if not ALLOWED_HOSTS:
    raise ValueError("ALLOWED_HOSTS 환경 변수가 설정되지 않았습니다!")

# 보안 설정
SECURE_SSL_REDIRECT = env('SECURE_SSL_REDIRECT', default=False)
SESSION_COOKIE_SECURE = env('SESSION_COOKIE_SECURE', default=False)
CSRF_COOKIE_SECURE = env('CSRF_COOKIE_SECURE', default=False)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# 데이터베이스 설정 - MariaDB (프로덕션 필수)
import pymysql
pymysql.install_as_MySQLdb()

# 데이터베이스 설정 - RDS 연결
# 환경 변수가 없으면 명시적으로 에러 발생
DB_NAME = env('DB_NAME', default=None)
DB_USER = env('DB_USER', default=None)
DB_PASSWORD = env('DB_PASSWORD', default=None)
DB_HOST = env('DB_HOST', default='localhost')
DB_PORT = env.int('DB_PORT', default=3306)

# 빈 값 체크
if not DB_NAME or not DB_USER or not DB_PASSWORD:
    missing_vars = []
    if not DB_NAME:
        missing_vars.append('DB_NAME')
    if not DB_USER:
        missing_vars.append('DB_USER')
    if not DB_PASSWORD:
        missing_vars.append('DB_PASSWORD')
    raise ValueError(
        f"데이터베이스 환경 변수가 설정되지 않았습니다: {', '.join(missing_vars)}. "
        f".env 파일 또는 환경 변수를 확인하세요."
    )

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES', character_set_connection=utf8mb4, collation_connection=utf8mb4_unicode_ci",
        },
    }
}

# Static files 설정 - S3 사용 (프로덕션)
# base.py의 STATIC_ROOT를 덮어쓰기 위해 명시적으로 설정
STATIC_ROOT = BASE_DIR / 'staticfiles'

USE_S3_STATIC = env('USE_S3_STATIC', default=False)

if USE_S3_STATIC:
    # S3를 사용하는 경우
    INSTALLED_APPS += ['storages']
    
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = env('AWS_STATIC_BUCKET_NAME')
    AWS_S3_REGION_NAME = env('AWS_REGION', default='ap-northeast-2')
    
    if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME]):
        raise ValueError("S3 Static files를 사용하려면 AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STATIC_BUCKET_NAME 환경 변수가 필요합니다!")
    
    # S3 커스텀 도메인 (STATIC_URL 계산에 필요)
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com'
    AWS_DEFAULT_ACL = None
      
    # Static files를 S3에 저장 (Manifest 기능 포함)
    # ManifestStaticStorage는 파일 내용의 해시를 파일명에 추가하여
    # CSS/JS 파일 변경 시 자동으로 새로운 URL이 생성되도록 합니다.
    STORAGES = {
        "staticfiles": {
            "BACKEND": "main.storages.ManifestStaticStorage",
        },
        # default는 Django 기본값 사용 (로컬 파일 시스템)
        # Media files를 S3에 저장하려면 MediaStorage 클래스를 추가하세요
    }
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    # STATIC_ROOT는 base.py에서 이미 설정되어 있지만, S3 사용 시에도 필요 (임시 저장용)
    
    # Media files도 S3를 사용하려면 아래 주석 해제
    # DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    # MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

    # S3 설정 완료 (로깅은 after_install.sh에서 처리)
    pass
else:
    # 로컬 파일 시스템 사용 (Manifest 기능 포함)
    # ManifestStaticFilesStorage를 사용하여 파일 변경 시 자동으로 URL이 변경되도록 함
    STORAGES = {
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
        },
    }
    STATIC_URL = '/static/'
    # STATIC_ROOT는 이미 base.py에서 설정됨
    pass

# 로깅 설정
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}

