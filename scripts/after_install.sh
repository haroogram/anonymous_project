#!/bin/bash

# AfterInstall 스크립트
# 배포 후 설치 및 설정 작업 수행
# NAT Gateway를 통해 인터넷 접근이 가능하므로 배포 시 패키지 설치/업데이트를 진행합니다.

# set -e를 사용하지 않음 (일부 명령이 실패해도 계속 진행)
# 대신 중요한 명령에만 에러 처리를 추가

echo "================================"
echo "AfterInstall 시작"
echo "================================"

APP_DIR="/home/ubuntu/anonymous_project"
VENV_DIR="/home/ubuntu/venv"

# Python 가상환경 확인 및 생성
if [ ! -d "$VENV_DIR" ]; then
    echo "⚠️  가상환경이 없습니다. 새로 생성합니다..."
    python3 -m venv $VENV_DIR || {
        echo "❌ 가상환경 생성 실패."
        exit 1
    }
    sudo chown -R ubuntu:ubuntu $VENV_DIR
    echo "✅ 가상환경 생성 완료"
else
    echo "✅ 기존 가상환경 발견"
fi

# 가상환경 활성화
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "❌ 가상환경 활성화 스크립트를 찾을 수 없습니다."
    exit 1
fi

echo "Python 가상환경 활성화..."
source $VENV_DIR/bin/activate

# requirements.txt 패키지 설치/업데이트 (매 배포마다 실행)
echo "================================"
echo "Python 패키지 설치/업데이트 중..."
echo "================================"

# pip 업그레이드
pip install --upgrade pip wheel --quiet || echo "⚠️  pip 업그레이드 실패 (계속 진행)"
pip install --upgrade "setuptools<81" --quiet || echo "⚠️  setuptools 설치 실패 (계속 진행)"

# requirements.txt 설치
if [ -f "$APP_DIR/requirements.txt" ]; then
    echo "requirements.txt 패키지 설치 중..."
    if pip install -r $APP_DIR/requirements.txt --quiet; then
        echo "✅ 패키지 설치 성공"
    else
        echo "❌ 패키지 설치 실패"
        echo "에러 상세 내용:"
        pip install -r $APP_DIR/requirements.txt 2>&1 | tail -n 20
        exit 1
    fi
else
    echo "❌ requirements.txt를 찾을 수 없습니다."
    exit 1
fi

# 설치된 주요 패키지 버전 확인
echo ""
echo "설치된 주요 패키지 버전:"
echo "  - Django: $(python -c "import django; print(django.get_version())" 2>/dev/null || echo "N/A")"
echo "  - gunicorn: $($VENV_DIR/bin/gunicorn --version 2>/dev/null || echo "N/A")"
echo "  - django-storages: $(pip show django-storages 2>/dev/null | grep Version | awk '{print $2}' || echo "N/A")"
echo "  - boto3: $(pip show boto3 2>/dev/null | grep Version | awk '{print $2}' || echo "N/A")"

# 로그 디렉토리 생성
mkdir -p $APP_DIR/logs
chmod 755 $APP_DIR/logs

# staticfiles 디렉토리 생성
mkdir -p $APP_DIR/staticfiles
chmod 755 $APP_DIR/staticfiles

# 작업 디렉토리로 이동
cd $APP_DIR

# 환경 변수 설정
export DJANGO_SETTINGS_MODULE=anonymous_project.settings.production

# .env 파일 확인 및 로드
if [ ! -f "$APP_DIR/.env" ]; then
    echo "⚠️  경고: .env 파일이 없습니다. 환경 변수를 확인하세요."
    echo "⚠️  DB 연결 및 migrations가 실패할 수 있습니다."
else
    echo "✅ .env 파일 확인됨"
    # .env 파일의 환경 변수 로드 (주석 제외)
    set -a
    source <(grep -v '^#' $APP_DIR/.env | sed 's/^/export /')
    set +a
fi

# Django static files 수집
echo "================================"
echo "Django static files 수집 중..."
echo "================================"
if python manage.py collectstatic --noinput --clear; then
    echo "✅ Static files 수집 성공"
else
    echo "❌ Static files 수집 실패"
    echo "에러 상세 내용:"
    python manage.py collectstatic --noinput --clear 2>&1 | tail -n 20
    echo "⚠️  Static files 수집 실패했지만 계속 진행합니다."
fi

# Django migrations 실행 (상세한 에러 확인)
echo "================================"
echo "데이터베이스 migrations 실행 중..."
echo "================================"

# DB 연결 테스트
echo "DB 연결 테스트 중..."
if python manage.py check --database default 2>&1 | grep -q "System check identified no issues"; then
    echo "✅ Django 시스템 체크 통과"
elif python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anonymous_project.settings.production')
django.setup()
from django.db import connection
connection.ensure_connection()
print('DB 연결 성공')
" 2>&1; then
    echo "✅ DB 연결 확인됨"
else
    echo "⚠️  DB 연결 확인 실패 (migrate 시도는 계속 진행)"
fi

# Migrations 실행
if python manage.py migrate --noinput --verbosity 2; then
    echo "✅ Migrations 실행 성공"
    
    # 생성된 테이블 확인
    echo "================================"
    echo "생성된 테이블 확인 중..."
    python manage.py showmigrations --list | grep -E "^\[X\]|^\[ \]" | head -n 20 || true
    echo "================================"
else
    echo "❌ Migrations 실행 실패"
    echo ""
    echo "================================"
    echo "에러 상세 내용:"
    echo "================================"
    python manage.py migrate --noinput --verbosity 2 2>&1 | tail -n 50
    
    echo ""
    echo "================================"
    echo "디버깅 정보:"
    echo "================================"
    echo "DB 설정 확인:"
    python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anonymous_project.settings.production')
django.setup()
from django.conf import settings
print(f'DB_NAME: {settings.DATABASES[\"default\"][\"NAME\"]}')
print(f'DB_USER: {settings.DATABASES[\"default\"][\"USER\"]}')
print(f'DB_HOST: {settings.DATABASES[\"default\"][\"HOST\"]}')
print(f'DB_PORT: {settings.DATABASES[\"default\"][\"PORT\"]}')
" 2>&1 || echo "DB 설정 확인 실패"
    
    echo ""
    echo "현재 적용된 migrations:"
    python manage.py showmigrations --list | head -n 30 || true
    
    echo ""
    echo "❌ Migrations가 실패했지만 배포는 계속 진행합니다."
    echo "⚠️  애플리케이션이 실행 중 에러가 발생할 수 있습니다."
    echo "⚠️  수동으로 migrate를 실행하세요:"
    echo "   cd $APP_DIR"
    echo "   source $VENV_DIR/bin/activate"
    echo "   export DJANGO_SETTINGS_MODULE=anonymous_project.settings.production"
    echo "   python manage.py migrate"
fi

# 환경 변수 파일 확인 (.env 파일은 서버에 별도로 설정되어 있어야 함)
if [ ! -f "$APP_DIR/.env" ]; then
    echo "경고: .env 파일이 없습니다. 환경 변수를 확인하세요."
fi

# 파일 권한 설정
sudo chown -R ubuntu:ubuntu $APP_DIR
chmod +x $APP_DIR/manage.py

# 가상환경 비활성화
deactivate

echo "AfterInstall 완료"

