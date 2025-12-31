#!/bin/bash
set -e

echo "================================"
echo "[6/8] Supervisor 설치"
echo "================================"

# 패키지 목록 업데이트
sudo DEBIAN_FRONTEND=noninteractive apt-get update -y

# Supervisor 설치 (프로세스 관리)
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y supervisor

# Supervisor 설정 디렉토리 확인
if [ ! -d /etc/supervisor/conf.d ]; then
    sudo mkdir -p /etc/supervisor/conf.d
fi

# 기본 Supervisor 설정 파일 생성 (템플릿)
sudo tee /etc/supervisor/conf.d/anonymous_project.conf > /dev/null <<EOF
; Django Gunicorn 프로세스 관리
[program:anonymous_project]
command=/home/ubuntu/venv/bin/gunicorn anonymous_project.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
directory=/home/ubuntu/app
user=ubuntu
autostart=false
autorestart=true
redirect_stderr=true
stdout_logfile=/home/ubuntu/app/logs/gunicorn.log
environment=DJANGO_SETTINGS_MODULE="anonymous_project.settings.production"

; Celery Worker (필요한 경우)
; [program:celery_worker]
; command=/home/ubuntu/venv/bin/celery -A anonymous_project worker --loglevel=info
; directory=/home/ubuntu/app
; user=ubuntu
; autostart=false
; autorestart=true
; redirect_stderr=true
; stdout_logfile=/home/ubuntu/app/logs/celery_worker.log

; Celery Beat (필요한 경우)
; [program:celery_beat]
; command=/home/ubuntu/venv/bin/celery -A anonymous_project beat --loglevel=info
; directory=/home/ubuntu/app
; user=ubuntu
; autostart=false
; autorestart=true
; redirect_stderr=true
; stdout_logfile=/home/ubuntu/app/logs/celery_beat.log
EOF

# Supervisor 설정 확인
sudo supervisorctl reread || true

# Supervisor 중지 (AMI에서는 시작하지 않음)
sudo systemctl stop supervisor || true
sudo systemctl disable supervisor || true

echo "✅ Supervisor 설치 및 기본 설정 완료"

