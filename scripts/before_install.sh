#!/bin/bash

# BeforeInstall 스크립트
# 배포 전 준비 작업 수행

set -e  # 에러 발생 시 스크립트 중단

echo "================================"
echo "BeforeInstall 시작"
echo "================================"

APP_DIR="/home/ubuntu/anonymous_project"
ENV_FILE="$APP_DIR/.env"

# AWS CLI 설치 확인 및 설치
if ! command -v aws &> /dev/null; then
    echo "AWS CLI가 설치되어 있지 않습니다. 설치 중..."
    
    # AWS CLI v2 설치 (Ubuntu)
    cd /tmp
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" || {
        echo "❌ AWS CLI 다운로드 실패"
        exit 1
    }
    unzip -q awscliv2.zip || {
        echo "❌ AWS CLI 압축 해제 실패"
        exit 1
    }
    sudo ./aws/install || {
        echo "❌ AWS CLI 설치 실패"
        exit 1
    }
    rm -rf awscliv2.zip aws/
    
    echo "✅ AWS CLI 설치 완료"
else
    echo "✅ AWS CLI 이미 설치됨: $(aws --version)"
fi

# 로그 디렉토리 생성
sudo mkdir -p $APP_DIR/logs
sudo chown -R ubuntu:ubuntu $APP_DIR/logs

# 이전 배포 디렉토리 백업 (선택사항)
if [ -d "$APP_DIR" ]; then
    echo "이전 배포 디렉토리 백업 중..."
    sudo cp -r $APP_DIR ${APP_DIR}_backup_$(date +%Y%m%d_%H%M%S) || true
fi

# 애플리케이션 디렉토리 생성 (없는 경우)
mkdir -p $APP_DIR

# ========================================
# AWS SSM Parameter Store에서 환경 변수 가져오기
# ========================================
echo "AWS SSM Parameter Store에서 환경 변수 가져오는 중..."

# AWS 리전 확인 (인스턴스 메타데이터에서 가져오거나 환경 변수 사용)
AWS_REGION="${AWS_REGION:-$(curl -s http://169.254.169.254/latest/meta-data/placement/region 2>/dev/null || echo 'ap-northeast-2')}"

# SSM 파라미터 베이스 경로 (필요에 따라 수정)
SSM_BASE_PATH="/anonymous-project"

# SSM 파라미터 가져오는 함수
get_ssm_parameter() {
    local param_name=$1
    local default_value=${2:-}
    local ssm_path="${SSM_BASE_PATH}/${param_name}"
    
    # 디버그 메시지는 stderr로 출력 (변수 할당 시 캡처되지 않도록)
    echo "  - ${param_name} 가져오는 중..." >&2
    
    # AWS CLI로 파라미터 가져오기 (WithDecryption으로 SecureString도 복호화)
    local value=$(aws ssm get-parameter \
        --name "$ssm_path" \
        --with-decryption \
        --region "$AWS_REGION" \
        --query 'Parameter.Value' \
        --output text 2>/dev/null || echo "")
    
    if [ -z "$value" ] && [ -n "$default_value" ]; then
        echo "    ⚠️  파라미터를 찾을 수 없어 기본값 사용: $default_value" >&2
        echo "$default_value"
    elif [ -n "$value" ]; then
        echo "    ✅ 파라미터 가져오기 성공" >&2
        echo "$value"
    else
        echo "    ❌ 파라미터를 찾을 수 없고 기본값도 없습니다" >&2
        echo ""
    fi
}

# 기존 .env 파일 백업 (있는 경우)
ENV_BACKUP_FILE="${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
if [ -f "$ENV_FILE" ]; then
    echo "기존 .env 파일 발견, 백업 중: $ENV_BACKUP_FILE"
    cp "$ENV_FILE" "$ENV_BACKUP_FILE"
    chmod 600 "$ENV_BACKUP_FILE"
fi

# 임시 파일에 새 .env 파일 생성 (실패 시 기존 파일 보존)
TEMP_ENV_FILE="${ENV_FILE}.tmp"
echo "환경 변수 파일 (.env) 생성 중 (임시 파일 사용)..."
cat > $TEMP_ENV_FILE <<EOF
# Django 프로덕션 환경 변수
# AWS SSM Parameter Store에서 자동으로 생성됨
# 생성 시간: $(date '+%Y-%m-%d %H:%M:%S')

EOF

# 환경 변수 로드 실패 시 플래그
ENV_LOAD_ERROR=false

# 필수 환경 변수들
SECRET_KEY=$(get_ssm_parameter "django/secret_key")
if [ -z "$SECRET_KEY" ]; then
    echo "❌ SECRET_KEY를 가져올 수 없습니다. SSM Parameter Store에 ${SSM_BASE_PATH}/secret_key가 설정되어 있는지 확인하세요."
    ENV_LOAD_ERROR=true
fi
echo "SECRET_KEY=$SECRET_KEY" >> $TEMP_ENV_FILE

ALLOWED_HOSTS=$(get_ssm_parameter "django/allowed_hosts")
if [ -z "$ALLOWED_HOSTS" ]; then
    echo "❌ ALLOWED_HOSTS를 가져올 수 없습니다. SSM Parameter Store에 ${SSM_BASE_PATH}/allowed_hosts가 설정되어 있는지 확인하세요."
    ENV_LOAD_ERROR=true
fi
echo "ALLOWED_HOSTS=$ALLOWED_HOSTS" >> $TEMP_ENV_FILE

# ALB 도메인 설정 (선택사항, ALB를 사용하는 경우)
ALB_DOMAIN=$(get_ssm_parameter "alb/domain")
if [ -n "$ALB_DOMAIN" ]; then
    echo "ALB_DOMAIN=$ALB_DOMAIN" >> $TEMP_ENV_FILE
    echo "✅ ALB 도메인 설정됨: $ALB_DOMAIN"
fi

# CSRF_TRUSTED_ORIGINS 설정 (선택사항)
CSRF_TRUSTED_ORIGINS=$(get_ssm_parameter "django/csrf-trusted-origins")
if [ -n "$CSRF_TRUSTED_ORIGINS" ]; then
    echo "CSRF_TRUSTED_ORIGINS=$CSRF_TRUSTED_ORIGINS" >> $TEMP_ENV_FILE
fi

# 데이터베이스 설정 (필수)
DB_NAME=$(get_ssm_parameter "db/name")
DB_USER=$(get_ssm_parameter "db/user")
DB_PASSWORD=$(get_ssm_parameter "db/password")
DB_HOST=$(get_ssm_parameter "db/host" "localhost")
DB_PORT=$(get_ssm_parameter "db/port" "3306")

if [ -z "$DB_NAME" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ]; then
    echo "❌ 데이터베이스 환경 변수를 가져올 수 없습니다. SSM Parameter Store에 다음 파라미터들이 설정되어 있는지 확인하세요:"
    echo "   - ${SSM_BASE_PATH}/db/name"
    echo "   - ${SSM_BASE_PATH}/db/user"
    echo "   - ${SSM_BASE_PATH}/db/password"
    ENV_LOAD_ERROR=true
fi

echo "DB_NAME=$DB_NAME" >> $TEMP_ENV_FILE
echo "DB_USER=$DB_USER" >> $TEMP_ENV_FILE
echo "DB_PASSWORD=$DB_PASSWORD" >> $TEMP_ENV_FILE
echo "DB_HOST=$DB_HOST" >> $TEMP_ENV_FILE
echo "DB_PORT=$DB_PORT" >> $TEMP_ENV_FILE

# Redis 설정
REDIS_HOST=$(get_ssm_parameter "redis/host" "localhost")
REDIS_PORT=$(get_ssm_parameter "redis/port" "6379")
REDIS_PASSWORD=$(get_ssm_parameter "redis/password")
REDIS_DB=$(get_ssm_parameter "redis/db" "0")

echo "REDIS_HOST=$REDIS_HOST" >> $TEMP_ENV_FILE
echo "REDIS_PORT=$REDIS_PORT" >> $TEMP_ENV_FILE
if [ -n "$REDIS_PASSWORD" ]; then
    echo "REDIS_PASSWORD=$REDIS_PASSWORD" >> $TEMP_ENV_FILE
fi
echo "REDIS_DB=$REDIS_DB" >> $TEMP_ENV_FILE

# 기타 설정 (선택사항)
DEBUG=$(get_ssm_parameter "debug" "False")
SECURE_SSL_REDIRECT=$(get_ssm_parameter "secure-ssl-redirect" "False")
SESSION_COOKIE_SECURE=$(get_ssm_parameter "session-cookie-secure" "False")
CSRF_COOKIE_SECURE=$(get_ssm_parameter "csrf-cookie-secure" "False")

echo "DEBUG=$DEBUG" >> $TEMP_ENV_FILE
echo "SECURE_SSL_REDIRECT=$SECURE_SSL_REDIRECT" >> $TEMP_ENV_FILE
echo "SESSION_COOKIE_SECURE=$SESSION_COOKIE_SECURE" >> $TEMP_ENV_FILE
echo "CSRF_COOKIE_SECURE=$CSRF_COOKIE_SECURE" >> $TEMP_ENV_FILE

# S3 Static files 설정 (선택사항)
USE_S3_STATIC=$(get_ssm_parameter "use-s3-static" "True")
AWS_ACCESS_KEY_ID=$(get_ssm_parameter "aws-access-key-id")
AWS_SECRET_ACCESS_KEY=$(get_ssm_parameter "aws-secret-access-key")
AWS_STATIC_BUCKET_NAME=$(get_ssm_parameter "aws-static-bucket-name")
# AWS_REGION=$(get_ssm_parameter "aws-region" "ap-northeast-2")

echo "USE_S3_STATIC=$USE_S3_STATIC" >> $TEMP_ENV_FILE
if [ -n "$AWS_ACCESS_KEY_ID" ]; then
    echo "AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID" >> $TEMP_ENV_FILE
fi
if [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY" >> $TEMP_ENV_FILE
fi
if [ -n "$AWS_STATIC_BUCKET_NAME" ]; then
    echo "AWS_STATIC_BUCKET_NAME=$AWS_STATIC_BUCKET_NAME" >> $TEMP_ENV_FILE
fi
echo "AWS_REGION=$AWS_REGION" >> $TEMP_ENV_FILE

# 에러 발생 시 처리
if [ "$ENV_LOAD_ERROR" = true ]; then
    echo ""
    echo "❌ 필수 환경 변수를 가져오는 데 실패했습니다."
    if [ -f "$ENV_FILE" ]; then
        echo "⚠️  기존 .env 파일을 유지합니다. ($ENV_FILE)"
        echo "⚠️  임시 파일 삭제: $TEMP_ENV_FILE"
        rm -f "$TEMP_ENV_FILE"
        echo ""
        echo "⚠️  주의: 기존 .env 파일을 사용하지만, SSM Parameter Store와 동기화되지 않았을 수 있습니다."
        echo "⚠️  SSM Parameter Store 설정을 확인하고 다시 배포하세요."
    else
        echo "❌ 기존 .env 파일도 없어 애플리케이션이 실행되지 않을 수 있습니다."
        echo "❌ SSM Parameter Store 설정을 확인하고 다시 배포하세요."
        rm -f "$TEMP_ENV_FILE"
        exit 1
    fi
else
    # 모든 환경 변수 로드 성공 - 임시 파일을 실제 .env 파일로 이동
    mv "$TEMP_ENV_FILE" "$ENV_FILE"
    chmod 600 "$ENV_FILE"
    chown ubuntu:ubuntu "$ENV_FILE"
    
    echo "✅ 환경 변수 파일 생성 완료: $ENV_FILE"
    echo "   (민감한 정보를 포함하므로 권한: 600)"
    
    # 이전 백업 파일 정리 (최근 3개만 유지)
    ls -t ${ENV_FILE}.backup.* 2>/dev/null | tail -n +4 | xargs rm -f 2>/dev/null || true
fi

# 필요한 시스템 패키지 설치 확인 (필요한 경우)
# sudo apt-get update
# sudo apt-get install -y python3-pip python3-venv nginx

# ========================================
# Supervisor 설치 및 설정 (packer AMI가 없는 경우에도 동작하도록 보강)
# ========================================
echo "Supervisor 설치 및 설정 확인 중..."

if ! command -v supervisorctl &> /dev/null; then
    echo "Supervisor가 설치되어 있지 않습니다. 설치 중..."
    sudo apt-get update -y
    sudo apt-get install -y supervisor
else
    echo "✅ Supervisor 이미 설치됨"
fi

# Supervisor 설정 디렉토리 보장
if [ ! -d /etc/supervisor/conf.d ]; then
    sudo mkdir -p /etc/supervisor/conf.d
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

# Supervisor 프로그램 설정 파일 생성/갱신
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

# Supervisor 서비스 활성화 및 재시작
sudo systemctl enable supervisor || true
sudo systemctl restart supervisor || sudo systemctl start supervisor || true

# Supervisor 설정 다시 읽기
sudo supervisorctl reread || true
sudo supervisorctl update || true

echo "✅ Supervisor 설치 및 설정 완료 (CodeDeploy 단계)"

echo "BeforeInstall 완료"

