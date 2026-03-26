#!/bin/bash
set -e

echo "==========================================="
echo "Django 애플리케이션 시작"
echo "==========================================="

# ========================================
# AWS SSM Parameter Store에서 환경 변수 가져오기 (.env 파일 생성)
# USE_SSM_ENV=true 인 경우에만 실행
# ========================================
if [ "$USE_SSM_ENV" = "true" ]; then
    echo "[0/4] AWS SSM Parameter Store에서 환경 변수 가져오는 중..."
    
    APP_DIR="/app"
    ENV_FILE="$APP_DIR/.env"
    
    # AWS 리전 확인
    AWS_REGION="${AWS_REGION:-ap-northeast-2}"
    
    # SSM 파라미터 베이스 경로
    SSM_BASE_PATH="${SSM_BASE_PATH:-/dso-project}"
    
    # 기존 .env 파일 백업
    if [ -f "$ENV_FILE" ]; then
        echo "기존 .env 파일 발견, 백업 중..."
        cp "$ENV_FILE" "${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # 임시 파일에 새 .env 파일 생성
    TEMP_ENV_FILE="${ENV_FILE}.tmp"
    cat > $TEMP_ENV_FILE <<EOF
# Django 프로덕션 환경 변수
# AWS SSM Parameter Store에서 자동으로 생성됨
# 생성 시간: $(date '+%Y-%m-%d %H:%M:%S')

EOF

    # .env에 안전하게 key=value를 기록합니다.
    # 값이 '$'로 시작하면 django-environ이 프록시 변수로 해석할 수 있어 '\$'로 이스케이프합니다.
    append_env_var() {
        local key="$1"
        local value="$2"
        if [[ "$value" == \$* ]]; then
            value="\\$value"
        fi
        printf "%s=%s\n" "$key" "$value" >> "$TEMP_ENV_FILE"
    }

    # 환경 변수 로드 실패 플래그
    ENV_LOAD_ERROR=false
    
    # ========================================
    # get-parameters-by-path로 한 번에 모든 파라미터 가져오기 (최적화)
    # ========================================
    echo "  SSM 파라미터 일괄 조회 중: ${SSM_BASE_PATH}/"
    
    SSM_RESULT=$(aws ssm get-parameters-by-path \
        --path "${SSM_BASE_PATH}/" \
        --recursive \
        --with-decryption \
        --region "$AWS_REGION" \
        --query 'Parameters[*].[Name,Value]' \
        --output text 2>/dev/null || echo "SSM_ERROR")
    
    if [ "$SSM_RESULT" = "SSM_ERROR" ] || [ -z "$SSM_RESULT" ]; then
        echo "❌ SSM 파라미터를 가져올 수 없습니다. IAM 권한 또는 경로를 확인하세요."
        ENV_LOAD_ERROR=true
    else
        echo "  ✅ SSM 파라미터 조회 성공"
        
        # 결과를 파싱하여 변수에 저장
        declare -A SSM_PARAMS
        while IFS=$'\t' read -r name value; do
            # 베이스 경로 제거하여 키 이름 추출
            key="${name#${SSM_BASE_PATH}/}"
            SSM_PARAMS["$key"]="$value"
            echo "    - $key: 로드됨"
        done <<< "$SSM_RESULT"
        
        # 필수 파라미터 확인 및 .env 파일 작성
        # Django 설정
        if [ -n "${SSM_PARAMS[django/secret_key]}" ]; then
            append_env_var "SECRET_KEY" "${SSM_PARAMS[django/secret_key]}"
        else
            echo "❌ SECRET_KEY를 가져올 수 없습니다."
            ENV_LOAD_ERROR=true
        fi
        
        if [ -n "${SSM_PARAMS[django/allowed_hosts]}" ]; then
            append_env_var "ALLOWED_HOSTS" "${SSM_PARAMS[django/allowed_hosts]}"
        else
            echo "❌ ALLOWED_HOSTS를 가져올 수 없습니다."
            ENV_LOAD_ERROR=true
        fi
        
        # /admin 접근 허용 IP 목록 (선택)
        [ -n "${SSM_PARAMS[django/admin_allowed_ips]}" ] && append_env_var "ADMIN_ALLOWED_IPS" "${SSM_PARAMS[django/admin_allowed_ips]}"
        
        # ALB 도메인 (선택)
        [ -n "${SSM_PARAMS[alb/domain]}" ] && append_env_var "ALB_DOMAIN" "${SSM_PARAMS[alb/domain]}"
        
        # CSRF (선택)
        [ -n "${SSM_PARAMS[django/csrf-trusted-origins]}" ] && append_env_var "CSRF_TRUSTED_ORIGINS" "${SSM_PARAMS[django/csrf-trusted-origins]}"
        
        # 데이터베이스 설정 (필수)
        if [ -n "${SSM_PARAMS[db/name]}" ] && [ -n "${SSM_PARAMS[db/user]}" ] && [ -n "${SSM_PARAMS[db/password]}" ]; then
            append_env_var "DB_NAME" "${SSM_PARAMS[db/name]}"
            append_env_var "DB_USER" "${SSM_PARAMS[db/user]}"
            append_env_var "DB_PASSWORD" "${SSM_PARAMS[db/password]}"
            append_env_var "DB_HOST" "${SSM_PARAMS[db/host]:-localhost}"
            append_env_var "DB_PORT" "${SSM_PARAMS[db/port]:-3306}"
        else
            echo "❌ 데이터베이스 환경 변수를 가져올 수 없습니다."
            ENV_LOAD_ERROR=true
        fi
        
        # Redis 설정
        append_env_var "REDIS_HOST" "${SSM_PARAMS[redis/host]:-localhost}"
        append_env_var "REDIS_PORT" "${SSM_PARAMS[redis/port]:-6379}"
        [ -n "${SSM_PARAMS[redis/password]}" ] && append_env_var "REDIS_PASSWORD" "${SSM_PARAMS[redis/password]}"
        append_env_var "REDIS_DB" "${SSM_PARAMS[redis/db]:-0}"
        append_env_var "REDIS_METRICS_DB" "${SSM_PARAMS[redis/metrics_db]:-1}"

        # Email(SMTP) 설정 (선택 - SES 등)
        [ -n "${SSM_PARAMS[email/backend]}" ] && append_env_var "EMAIL_BACKEND" "${SSM_PARAMS[email/backend]}"
        [ -n "${SSM_PARAMS[email/host]}" ] && append_env_var "EMAIL_HOST" "${SSM_PARAMS[email/host]}"
        [ -n "${SSM_PARAMS[email/port]}" ] && append_env_var "EMAIL_PORT" "${SSM_PARAMS[email/port]}"
        [ -n "${SSM_PARAMS[email/use_tls]}" ] && append_env_var "EMAIL_USE_TLS" "${SSM_PARAMS[email/use_tls]}"
        [ -n "${SSM_PARAMS[email/default_from]}" ] && append_env_var "DEFAULT_FROM_EMAIL" "${SSM_PARAMS[email/default_from]}"
        [ -n "${SSM_PARAMS[email/smtp_username]}" ] && append_env_var "EMAIL_HOST_USER" "${SSM_PARAMS[email/smtp_username]}"
        [ -n "${SSM_PARAMS[email/smtp_password]}" ] && append_env_var "EMAIL_HOST_PASSWORD" "${SSM_PARAMS[email/smtp_password]}"
        
        # 기타 설정
        append_env_var "DEBUG" "${SSM_PARAMS[debug]:-False}"
        append_env_var "SECURE_SSL_REDIRECT" "${SSM_PARAMS[secure-ssl-redirect]:-False}"
        append_env_var "SESSION_COOKIE_SECURE" "${SSM_PARAMS[session-cookie-secure]:-True}"
        append_env_var "CSRF_COOKIE_SECURE" "${SSM_PARAMS[csrf-cookie-secure]:-True}"
        
        # S3 Static files 설정
        append_env_var "USE_S3_STATIC" "${SSM_PARAMS[use-s3-static]:-False}"
        # S3 사용자 업로드(자유게시판 첨부 등) — USE_S3_STATIC=true 및 버킷 설정과 함께 사용
        append_env_var "USE_S3_MEDIA" "${SSM_PARAMS[use-s3-media]:-False}"
        [ -n "${SSM_PARAMS[aws-access-key-id]}" ] && append_env_var "AWS_ACCESS_KEY_ID" "${SSM_PARAMS[aws-access-key-id]}"
        [ -n "${SSM_PARAMS[aws-secret-access-key]}" ] && append_env_var "AWS_SECRET_ACCESS_KEY" "${SSM_PARAMS[aws-secret-access-key]}"
        [ -n "${SSM_PARAMS[app/static_bucket]}" ] && append_env_var "AWS_STATIC_BUCKET_NAME" "${SSM_PARAMS[app/static_bucket]}"
        append_env_var "AWS_REGION" "$AWS_REGION"
    fi
    
    # 에러 발생 시 처리
    if [ "$ENV_LOAD_ERROR" = true ]; then
        echo ""
        echo "❌ 필수 환경 변수를 가져오는 데 실패했습니다."
        if [ -f "$ENV_FILE" ]; then
            echo "⚠️  기존 .env 파일을 유지합니다."
            rm -f "$TEMP_ENV_FILE"
        else
            echo "❌ 기존 .env 파일도 없어 애플리케이션이 실행되지 않을 수 있습니다."
            rm -f "$TEMP_ENV_FILE"
            exit 1
        fi
    else
        mv "$TEMP_ENV_FILE" "$ENV_FILE"
        chmod 600 "$ENV_FILE"
        echo "✅ 환경 변수 파일 생성 완료: $ENV_FILE"
        
        # 이전 백업 파일 정리 (최근 3개만 유지)
        ls -t ${ENV_FILE}.backup.* 2>/dev/null | tail -n +4 | xargs rm -f 2>/dev/null || true
    fi
else
    echo "[0/4] SSM 환경 변수 로드 건너뜀 (USE_SSM_ENV=true로 활성화)"
fi

# 1. 데이터베이스 연결 확인 (로그 남기기)
echo "[1/4] 데이터베이스 연결 확인..."
python - << 'PY'
import django
import logging
from django.db import connections
from django.db.utils import OperationalError

django.setup()
logger = logging.getLogger('django.db')

try:
    conn = connections['default']
    conn.cursor()
    logger.warning("DB connection check succeeded for 'default' database.")
except OperationalError as e:
    logger.error("DB connection check failed for 'default' database: %s", e)
    raise
PY

# 2. 데이터베이스 마이그레이션
echo "[2/4] 데이터베이스 마이그레이션 실행..."
python manage.py migrate --noinput

# 2. 초기 데이터 로드 (실패해도 계속 진행)
echo "[3/4] 초기 데이터 로드..."
python manage.py load_initial_data || echo "⚠ 초기 데이터가 이미 존재하거나 로드 실패 (계속 진행)"

# 3. 정적 파일 수집
echo "[4/4] 정적 파일 수집..."
python manage.py collectstatic --noinput --clear || echo "⚠ collectstatic 실패 (계속 진행)"

echo "==========================================="
echo "✓ 초기화 완료, Gunicorn 시작"
echo "==========================================="

# 4. Gunicorn 실행
exec gunicorn --bind 0.0.0.0:8000 --workers 3 anonymous_project.wsgi:application
