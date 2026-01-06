#!/bin/bash

# ApplicationStart 스크립트
# 애플리케이션 시작

set -e  # 에러 발생 시 스크립트 중단

echo "================================"
echo "ApplicationStart 시작"
echo "================================"

APP_DIR="/home/ubuntu/anonymous_project"
VENV_DIR="/home/ubuntu/venv"

# 가상환경 활성화
source $VENV_DIR/bin/activate

cd $APP_DIR

# 환경 변수 설정
export DJANGO_SETTINGS_MODULE=anonymous_project.settings.production

# Gunicorn을 사용하는 경우 (필요에 따라 변경)
# 기존 프로세스가 있으면 종료
if pgrep -f "gunicorn" > /dev/null; then
    echo "기존 Gunicorn 프로세스 종료 중..."
    pkill -f gunicorn || true
    sleep 2
fi

# Gunicorn 시작 (포트와 워커 수는 환경에 맞게 조정)
# 주석 해제하고 필요에 따라 수정
# nohup gunicorn \
#     --bind 0.0.0.0:8000 \
#     --workers 3 \
#     --timeout 120 \
#     --access-logfile $APP_DIR/logs/gunicorn_access.log \
#     --error-logfile $APP_DIR/logs/gunicorn_error.log \
#     --log-level info \
#     --daemon \
#     anonymous_project.wsgi:application

# 또는 Supervisor를 사용하는 경우 (권장)
# Supervisor 설정 파일이 /etc/supervisor/conf.d/ 아래에 있다고 가정
if command -v supervisorctl &> /dev/null; then
    echo "Supervisor로 애플리케이션 시작 중..."
    # 먼저 상태 확인
    status=$(sudo supervisorctl status anonymous_project 2>/dev/null || echo "")
    if echo "$status" | grep -q "RUNNING"; then
        echo "애플리케이션이 이미 실행 중입니다. 재시작합니다..."
        sudo supervisorctl restart anonymous_project
    else
        echo "애플리케이션을 시작합니다..."
        sudo supervisorctl start anonymous_project
    fi
    
    # 시작 확인 (최대 30초 대기)
    echo "애플리케이션 시작 대기 중..."
    for i in {1..30}; do
        if sudo supervisorctl status anonymous_project 2>/dev/null | grep -q "RUNNING"; then
            echo "✅ 애플리케이션이 시작되었습니다."
            sleep 2  # 포트 바인딩을 위한 추가 대기
            break
        fi
        sleep 1
    done
fi

# 또는 systemd를 사용하는 경우
if systemctl is-active --quiet anonymous_project.service 2>/dev/null; then
    echo "systemd로 애플리케이션 재시작 중..."
    sudo systemctl restart anonymous_project.service || true
else
    echo "systemd 서비스가 설정되지 않았습니다."
fi

# Celery Worker 및 Beat 시작 (필요한 경우)
if command -v supervisorctl &> /dev/null; then
    echo "Celery 서비스 재시작 중..."
    sudo supervisorctl restart celery_worker || sudo supervisorctl start celery_worker || true
    sudo supervisorctl restart celery_beat || sudo supervisorctl start celery_beat || true
fi

deactivate

echo "ApplicationStart 완료"

