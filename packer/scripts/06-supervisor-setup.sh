#!/bin/bash
set -e

echo "================================"
echo "[6/8] Supervisor 설치"
echo "================================"

# Supervisor 설치 (프로세스 관리)
# 참고: apt-get update는 01-base-setup.sh에서 이미 실행됨
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
directory=/home/ubuntu/anonymous_project
user=ubuntu
autostart=false
autorestart=true
redirect_stderr=true
stdout_logfile=/home/ubuntu/anonymous_project/logs/gunicorn.log
environment=DJANGO_SETTINGS_MODULE="anonymous_project.settings.production"

; Celery Worker (필요한 경우)
[program:celery_worker]
command=/home/ubuntu/venv/bin/celery -A anonymous_project worker --loglevel=info
directory=/home/ubuntu/anonymous_project
user=ubuntu
autostart=false
autorestart=true
redirect_stderr=true
stdout_logfile=/home/ubuntu/anonymous_project/logs/celery_worker.log

; Celery Beat (필요한 경우)
[program:celery_beat]
command=/home/ubuntu/venv/bin/celery -A anonymous_project beat --loglevel=info
directory=/home/ubuntu/anonymous_project
user=ubuntu
autostart=false
autorestart=true
redirect_stderr=true
stdout_logfile=/home/ubuntu/anonymous_project/logs/celery_beat.log
EOF

# Supervisor 설정 확인
sudo supervisorctl reread || true

# Supervisor 서비스 활성화 및 시작 (AMI에서 enable 상태로 유지, EC2 시작 시 자동 실행)
# ASG health check가 정상 응답을 받기 위해 필요
sudo systemctl enable supervisor
sudo systemctl start supervisor || true
echo "✅ Supervisor 서비스 활성화 및 시작 완료"

echo "✅ Supervisor 설치 및 기본 설정 완료"
echo "✅ Supervisor가 enable 상태로 설정되어 EC2 시작 시 자동 실행됩니다."
