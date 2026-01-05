#!/bin/bash

# AfterInstall 스크립트
# 배포 후 설치 및 설정 작업 수행
# 주의: EC2는 인터넷 접근이 불가능하므로 AMI에 미리 설치된 패키지를 사용합니다.

# set -e를 사용하지 않음 (인터넷 접근 불가 시 일부 명령이 실패할 수 있음)
# 대신 중요한 명령에만 에러 처리를 추가

echo "================================"
echo "AfterInstall 시작"
echo "================================"

APP_DIR="/home/ubuntu/anonymous_project"
VENV_DIR="/home/ubuntu/venv"

# Python 가상환경 확인
if [ ! -d "$VENV_DIR" ]; then
    echo "⚠️  가상환경이 없습니다. AMI에 가상환경이 포함되어 있어야 합니다."
    echo "가상환경 생성 시도 중... (인터넷 접근 불가 시 실패할 수 있음)"
    python3 -m venv $VENV_DIR || {
        echo "❌ 가상환경 생성 실패. AMI에 가상환경이 포함되어 있는지 확인하세요."
        exit 1
    }
    echo "⚠️  새 가상환경이 생성되었습니다. 패키지 설치를 시도하지만 인터넷 접근 불가 시 실패할 수 있습니다."
    NEED_INSTALL=true
else
    echo "✅ 기존 가상환경 발견 (AMI에 미리 설치됨)"
    echo "   인터넷 접근 없이 기존 패키지를 사용합니다."
    NEED_INSTALL=false
fi

# 가상환경 활성화
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "❌ 가상환경 활성화 스크립트를 찾을 수 없습니다."
    exit 1
fi

echo "Python 가상환경 활성화..."
source $VENV_DIR/bin/activate

# 가상환경이 이미 존재하는 경우 (AMI에 미리 설치됨)
# pip 업그레이드나 패키지 설치를 시도하지 않음 (인터넷 접근 불가)
if [ "$NEED_INSTALL" = false ]; then
    echo "✅ AMI에 설치된 패키지 사용 중"
    echo "   gunicorn 버전 확인:"
    $VENV_DIR/bin/gunicorn --version || echo "⚠️  gunicorn을 찾을 수 없습니다."
    echo "   Django 버전 확인:"
    python -c "import django; print(django.get_version())" || echo "⚠️  Django를 찾을 수 없습니다."
else
    # 새로 생성된 가상환경인 경우에만 설치 시도 (인터넷 접근 불가 시 실패)
    echo "⚠️  새 가상환경에 패키지 설치 시도 중..."
    echo "   (인터넷 접근 불가 시 실패할 수 있음)"
    
    # pip 업그레이드 시도 (실패해도 계속 진행)
    pip install --upgrade pip setuptools wheel 2>&1 | grep -v "WARNING" || echo "⚠️  pip 업그레이드 실패 (계속 진행)"
    
    # requirements.txt 설치 시도 (실패해도 계속 진행)
    if [ -f "$APP_DIR/requirements.txt" ]; then
        cd $APP_DIR
        pip install -r requirements.txt 2>&1 | grep -v "WARNING" || {
            echo "❌ 패키지 설치 실패 (인터넷 접근 불가)"
            echo "   AMI에 패키지가 미리 설치되어 있어야 합니다."
            exit 1
        }
    else
        echo "❌ requirements.txt를 찾을 수 없습니다."
        exit 1
    fi
fi

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

