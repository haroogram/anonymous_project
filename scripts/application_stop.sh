#!/bin/bash

# ApplicationStop 스크립트
# 애플리케이션 종료

set -e  # 에러 발생 시 스크립트 중단

echo "================================"
echo "ApplicationStop 시작"
echo "================================"

# Supervisor를 사용하는 경우
if command -v supervisorctl &> /dev/null; then
    echo "Supervisor로 애플리케이션 중지 중..."
    sudo supervisorctl stop anonymous_project || true
    sudo supervisorctl stop celery_worker || true
    sudo supervisorctl stop celery_beat || true
fi

# systemd를 사용하는 경우
if systemctl is-active --quiet anonymous_project.service 2>/dev/null; then
    echo "systemd로 애플리케이션 중지 중..."
    sudo systemctl stop anonymous_project.service || true
fi

# Gunicorn 프로세스 직접 종료 (fallback)
if pgrep -f "gunicorn" > /dev/null; then
    echo "Gunicorn 프로세스 종료 중..."
    pkill -f gunicorn || true
    sleep 2
    
    # 강제 종료 (필요한 경우)
    if pgrep -f "gunicorn" > /dev/null; then
        pkill -9 -f gunicorn || true
    fi
fi

# Celery 프로세스 종료
if pgrep -f "celery" > /dev/null; then
    echo "Celery 프로세스 종료 중..."
    pkill -f "celery worker" || true
    pkill -f "celery beat" || true
    sleep 2
fi

echo "ApplicationStop 완료"

