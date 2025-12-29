#!/bin/bash

# AfterInstall 스크립트
# 배포 후 설치 및 설정 작업 수행

set -e  # 에러 발생 시 스크립트 중단

echo "================================"
echo "AfterInstall 시작"
echo "================================"

APP_DIR="/home/ubuntu/app"
VENV_DIR="/home/ubuntu/venv"

# Python 가상환경 생성 또는 활성화
if [ ! -d "$VENV_DIR" ]; then
    echo "Python 가상환경 생성 중..."
    python3 -m venv $VENV_DIR
fi

echo "Python 가상환경 활성화..."
source $VENV_DIR/bin/activate

# pip 업그레이드
echo "pip 업그레이드 중..."
pip install --upgrade pip setuptools wheel

# requirements.txt 설치
echo "Python 패키지 설치 중..."
cd $APP_DIR
pip install -r requirements.txt

# 로그 디렉토리 생성
mkdir -p $APP_DIR/logs
chmod 755 $APP_DIR/logs

# staticfiles 디렉토리 생성
mkdir -p $APP_DIR/staticfiles
chmod 755 $APP_DIR/staticfiles

# Django static files 수집
echo "Static files 수집 중..."
export DJANGO_SETTINGS_MODULE=anonymous_project.settings.production
python manage.py collectstatic --noinput --clear || true

# Django migrations 실행
echo "데이터베이스 migrations 실행 중..."
python manage.py migrate --noinput || true

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

