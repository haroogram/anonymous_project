#!/bin/bash
# Ubuntu 22.04 LTS 환경용 Supervisor 설치 스크립트
set -e

# Ubuntu/Debian 계열 시스템에서 비대화형 모드 설정
export DEBIAN_FRONTEND=noninteractive

echo "================================"
echo "[6/8] Supervisor 설치"
echo "================================"

# Supervisor 설치 (프로세스 관리)
# 참고: apt-get update는 01-base-setup.sh에서 이미 실행됨
sudo apt-get install -y supervisor

# Supervisor 설정 디렉토리 확인
if [ ! -d /etc/supervisor/conf.d ]; then
    sudo mkdir -p /etc/supervisor/conf.d
fi

# 애플리케이션 디렉토리 생성 (07-directories-setup.sh보다 먼저 실행되므로 여기서 생성)
APP_DIR="/home/ubuntu/anonymous_project"
if [ ! -d "$APP_DIR" ]; then
    echo "애플리케이션 디렉토리 생성 중..."
    sudo mkdir -p "$APP_DIR"
    sudo mkdir -p "$APP_DIR/logs"
    sudo chown -R ubuntu:ubuntu "$APP_DIR"
fi

# Gunicorn wrapper 스크립트 생성 (.env 파일 로드)
sudo tee /home/ubuntu/anonymous_project/gunicorn_wrapper.sh > /dev/null <<'GUNICORN_EOF'
#!/bin/bash
# Gunicorn wrapper - .env 파일 로드 후 gunicorn 실행
APP_DIR="/home/ubuntu/anonymous_project"
VENV_DIR="/home/ubuntu/venv"

# .env 파일이 있으면 안전하게 로드 (특수문자 처리)
if [ -f "$APP_DIR/.env" ]; then
    # .env 파일을 안전하게 파싱하여 환경 변수로 설정
    while IFS= read -r line || [ -n "$line" ]; do
        # 주석이나 빈 줄 건너뛰기
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "$line" ]] && continue
        
        # 첫 번째 = 기준으로 key와 value 분리 (값에 =가 포함될 수 있음)
        if [[ "$line" =~ ^([^=]+)=(.*)$ ]]; then
            key="${BASH_REMATCH[1]}"
            value="${BASH_REMATCH[2]}"
            
            # 앞뒤 공백 제거
            key=$(echo "$key" | xargs)
            value=$(echo "$value" | xargs)
            
            # 값이 있으면 환경 변수로 설정 (값에 특수문자가 있어도 안전하게 처리)
            if [ -n "$key" ] && [ -n "$value" ]; then
                export "$key"="$value"
            fi
        fi
    done < "$APP_DIR/.env"
fi

# 환경 변수 설정
export DJANGO_SETTINGS_MODULE=anonymous_project.settings.production

# Gunicorn 실행
exec "$VENV_DIR/bin/gunicorn" anonymous_project.wsgi:application "$@"
GUNICORN_EOF

sudo chmod +x /home/ubuntu/anonymous_project/gunicorn_wrapper.sh
sudo chown ubuntu:ubuntu /home/ubuntu/anonymous_project/gunicorn_wrapper.sh

# Celery wrapper 스크립트 생성
sudo tee /home/ubuntu/anonymous_project/celery_wrapper.sh > /dev/null <<'CELERY_EOF'
#!/bin/bash
# Celery wrapper - .env 파일 로드 후 celery 실행
APP_DIR="/home/ubuntu/anonymous_project"
VENV_DIR="/home/ubuntu/venv"

# .env 파일이 있으면 안전하게 로드 (특수문자 처리)
if [ -f "$APP_DIR/.env" ]; then
    # .env 파일을 안전하게 파싱하여 환경 변수로 설정
    while IFS= read -r line || [ -n "$line" ]; do
        # 주석이나 빈 줄 건너뛰기
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "$line" ]] && continue
        
        # 첫 번째 = 기준으로 key와 value 분리 (값에 =가 포함될 수 있음)
        if [[ "$line" =~ ^([^=]+)=(.*)$ ]]; then
            key="${BASH_REMATCH[1]}"
            value="${BASH_REMATCH[2]}"
            
            # 앞뒤 공백 제거
            key=$(echo "$key" | xargs)
            value=$(echo "$value" | xargs)
            
            # 값이 있으면 환경 변수로 설정 (값에 특수문자가 있어도 안전하게 처리)
            if [ -n "$key" ] && [ -n "$value" ]; then
                export "$key"="$value"
            fi
        fi
    done < "$APP_DIR/.env"
fi

# 환경 변수 설정
export DJANGO_SETTINGS_MODULE=anonymous_project.settings.production

# Celery 실행
exec "$VENV_DIR/bin/celery" -A anonymous_project "$@"
CELERY_EOF

sudo chmod +x /home/ubuntu/anonymous_project/celery_wrapper.sh
sudo chown ubuntu:ubuntu /home/ubuntu/anonymous_project/celery_wrapper.sh

# 기본 Supervisor 설정 파일 생성 (템플릿)
sudo tee /etc/supervisor/conf.d/anonymous_project.conf > /dev/null <<EOF
; Django Gunicorn 프로세스 관리
[program:anonymous_project]
command=/home/ubuntu/anonymous_project/gunicorn_wrapper.sh --bind 0.0.0.0:8000 --workers 3 --timeout 120
directory=/home/ubuntu/anonymous_project
user=ubuntu
autostart=false
autorestart=true
redirect_stderr=true
stdout_logfile=/home/ubuntu/anonymous_project/logs/gunicorn.log

; Celery Worker (필요한 경우)
[program:celery_worker]
command=/home/ubuntu/anonymous_project/celery_wrapper.sh worker --loglevel=info
directory=/home/ubuntu/anonymous_project
user=ubuntu
autostart=false
autorestart=true
redirect_stderr=true
stdout_logfile=/home/ubuntu/anonymous_project/logs/celery_worker.log

; Celery Beat (필요한 경우)
[program:celery_beat]
command=/home/ubuntu/anonymous_project/celery_wrapper.sh beat --loglevel=info
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
