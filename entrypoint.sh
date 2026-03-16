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
            echo "SECRET_KEY=${SSM_PARAMS[django/secret_key]}" >> $TEMP_ENV_FILE
        else
            echo "❌ SECRET_KEY를 가져올 수 없습니다."
            ENV_LOAD_ERROR=true
        fi
        
        if [ -n "${SSM_PARAMS[django/allowed_hosts]}" ]; then
            echo "ALLOWED_HOSTS=${SSM_PARAMS[django/allowed_hosts]}" >> $TEMP_ENV_FILE
        else
            echo "❌ ALLOWED_HOSTS를 가져올 수 없습니다."
            ENV_LOAD_ERROR=true
        fi
        
        # ALB 도메인 (선택)
        [ -n "${SSM_PARAMS[alb/domain]}" ] && echo "ALB_DOMAIN=${SSM_PARAMS[alb/domain]}" >> $TEMP_ENV_FILE
        
        # CSRF (선택)
        [ -n "${SSM_PARAMS[django/csrf-trusted-origins]}" ] && echo "CSRF_TRUSTED_ORIGINS=${SSM_PARAMS[django/csrf-trusted-origins]}" >> $TEMP_ENV_FILE
        
        # 데이터베이스 설정 (필수)
        if [ -n "${SSM_PARAMS[db/name]}" ] && [ -n "${SSM_PARAMS[db/user]}" ] && [ -n "${SSM_PARAMS[db/password]}" ]; then
            echo "DB_NAME=${SSM_PARAMS[db/name]}" >> $TEMP_ENV_FILE
            echo "DB_USER=${SSM_PARAMS[db/user]}" >> $TEMP_ENV_FILE
            echo "DB_PASSWORD=${SSM_PARAMS[db/password]}" >> $TEMP_ENV_FILE
            echo "DB_HOST=${SSM_PARAMS[db/host]:-localhost}" >> $TEMP_ENV_FILE
            echo "DB_PORT=${SSM_PARAMS[db/port]:-3306}" >> $TEMP_ENV_FILE
        else
            echo "❌ 데이터베이스 환경 변수를 가져올 수 없습니다."
            ENV_LOAD_ERROR=true
        fi
        
        # Redis 설정
        echo "REDIS_HOST=${SSM_PARAMS[redis/host]:-localhost}" >> $TEMP_ENV_FILE
        echo "REDIS_PORT=${SSM_PARAMS[redis/port]:-6379}" >> $TEMP_ENV_FILE
        [ -n "${SSM_PARAMS[redis/password]}" ] && echo "REDIS_PASSWORD=${SSM_PARAMS[redis/password]}" >> $TEMP_ENV_FILE
        echo "REDIS_DB=${SSM_PARAMS[redis/db]:-0}" >> $TEMP_ENV_FILE
        
        # 기타 설정
        echo "DEBUG=${SSM_PARAMS[debug]:-False}" >> $TEMP_ENV_FILE
        echo "SECURE_SSL_REDIRECT=${SSM_PARAMS[secure-ssl-redirect]:-False}" >> $TEMP_ENV_FILE
        echo "SESSION_COOKIE_SECURE=${SSM_PARAMS[session-cookie-secure]:-True}" >> $TEMP_ENV_FILE
        echo "CSRF_COOKIE_SECURE=${SSM_PARAMS[csrf-cookie-secure]:-True}" >> $TEMP_ENV_FILE
        
        # S3 Static files 설정
        echo "USE_S3_STATIC=${SSM_PARAMS[use-s3-static]:-False}" >> $TEMP_ENV_FILE
        [ -n "${SSM_PARAMS[aws-access-key-id]}" ] && echo "AWS_ACCESS_KEY_ID=${SSM_PARAMS[aws-access-key-id]}" >> $TEMP_ENV_FILE
        [ -n "${SSM_PARAMS[aws-secret-access-key]}" ] && echo "AWS_SECRET_ACCESS_KEY=${SSM_PARAMS[aws-secret-access-key]}" >> $TEMP_ENV_FILE
        [ -n "${SSM_PARAMS[app/static_bucket]}" ] && echo "AWS_STATIC_BUCKET_NAME=${SSM_PARAMS[app/static_bucket]}" >> $TEMP_ENV_FILE
        echo "AWS_REGION=$AWS_REGION" >> $TEMP_ENV_FILE
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

# 1. 데이터베이스 마이그레이션
echo "[1/4] 데이터베이스 마이그레이션 실행..."
python manage.py migrate --noinput

# 2. 초기 데이터 로드 (실패해도 계속 진행)
echo "[2/4] 초기 데이터 로드..."
python manage.py load_initial_data || echo "⚠ 초기 데이터가 이미 존재하거나 로드 실패 (계속 진행)"

# 3. 정적 파일 수집
echo "[3/4] 정적 파일 수집..."
python manage.py collectstatic --noinput --clear || echo "⚠ collectstatic 실패 (계속 진행)"

echo "==========================================="
echo "✓ 초기화 완료, Gunicorn 시작"
echo "==========================================="

# 4. Gunicorn 실행
exec gunicorn --bind 0.0.0.0:8000 --workers 3 anonymous_project.wsgi:application
