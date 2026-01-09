#!/bin/bash

# AfterInstall 스크립트
# 배포 후 설치 및 설정 작업 수행
# NAT Gateway를 통해 인터넷 접근이 가능하므로 배포 시 패키지 설치/업데이트를 진행합니다.

# set -e를 사용하지 않음 (일부 명령이 실패해도 계속 진행)
# 대신 중요한 명령에만 에러 처리를 추가

echo "================================"
echo "AfterInstall 시작"
echo "================================"

APP_DIR="/home/ubuntu/anonymous_project"
VENV_DIR="/home/ubuntu/venv"

# Python 가상환경 확인 및 생성
if [ ! -d "$VENV_DIR" ]; then
    echo "⚠️  가상환경이 없습니다. 새로 생성합니다..."
    python3 -m venv $VENV_DIR || {
        echo "❌ 가상환경 생성 실패."
        exit 1
    }
    sudo chown -R ubuntu:ubuntu $VENV_DIR
    echo "✅ 가상환경 생성 완료"
else
    echo "✅ 기존 가상환경 발견"
fi

# 가상환경 활성화
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "❌ 가상환경 활성화 스크립트를 찾을 수 없습니다."
    exit 1
fi

echo "Python 가상환경 활성화..."
source $VENV_DIR/bin/activate

# requirements.txt 패키지 설치/업데이트 (매 배포마다 실행)
echo "================================"
echo "Python 패키지 설치/업데이트 중..."
echo "================================"

# pip 업그레이드
pip install --upgrade pip wheel --quiet || echo "⚠️  pip 업그레이드 실패 (계속 진행)"
pip install --upgrade "setuptools<81" --quiet || echo "⚠️  setuptools 설치 실패 (계속 진행)"

# requirements.txt 설치
if [ -f "$APP_DIR/requirements.txt" ]; then
    echo "requirements.txt 패키지 설치 중..."
    if pip install -r $APP_DIR/requirements.txt --quiet; then
        echo "✅ 패키지 설치 성공"
    else
        echo "❌ 패키지 설치 실패"
        echo "에러 상세 내용:"
        pip install -r $APP_DIR/requirements.txt 2>&1 | tail -n 20
        exit 1
    fi
else
    echo "❌ requirements.txt를 찾을 수 없습니다."
    exit 1
fi

# 설치된 주요 패키지 버전 확인
echo ""
echo "설치된 주요 패키지 버전:"
echo "  - Django: $(python -c "import django; print(django.get_version())" 2>/dev/null || echo "N/A")"
echo "  - gunicorn: $($VENV_DIR/bin/gunicorn --version 2>/dev/null || echo "N/A")"
echo "  - django-storages: $(pip show django-storages 2>/dev/null | grep Version | awk '{print $2}' || echo "N/A")"
echo "  - boto3: $(pip show boto3 2>/dev/null | grep Version | awk '{print $2}' || echo "N/A")"

# 로그 디렉토리 생성
mkdir -p $APP_DIR/logs
chmod 755 $APP_DIR/logs

# staticfiles 디렉토리 생성
mkdir -p $APP_DIR/staticfiles
chmod 755 $APP_DIR/staticfiles

# 작업 디렉토리로 이동
cd $APP_DIR

# 환경 변수 설정
export DJANGO_SETTINGS_MODULE=anonymous_project.settings.production

# .env 파일 확인 및 로드
if [ ! -f "$APP_DIR/.env" ]; then
    echo "⚠️  경고: .env 파일이 없습니다. 환경 변수를 확인하세요."
    echo "⚠️  DB 연결 및 migrations가 실패할 수 있습니다."
    echo ""
    echo "필수 환경 변수:"
    echo "  - DB_NAME: RDS 데이터베이스 이름"
    echo "  - DB_USER: RDS 사용자 이름"
    echo "  - DB_PASSWORD: RDS 비밀번호"
    echo "  - DB_HOST: RDS 엔드포인트"
    echo "  - DB_PORT: RDS 포트 (기본값: 3306)"
    echo "  - SECRET_KEY: Django SECRET_KEY"
    echo "  - ALLOWED_HOSTS: 허용된 호스트 (쉼표 구분)"
else
    echo "✅ .env 파일 확인됨"
    # .env 파일의 환경 변수 로드 (특수문자 안전하게 처리)
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
    
    # 필수 환경 변수 확인
    echo ""
    echo "환경 변수 확인 중..."
    MISSING_VARS=()
    if [ -z "$DB_NAME" ]; then
        MISSING_VARS+=("DB_NAME")
    fi
    if [ -z "$DB_USER" ]; then
        MISSING_VARS+=("DB_USER")
    fi
    if [ -z "$DB_PASSWORD" ]; then
        MISSING_VARS+=("DB_PASSWORD")
    fi
    if [ -z "$SECRET_KEY" ]; then
        MISSING_VARS+=("SECRET_KEY")
    fi
    if [ -z "$ALLOWED_HOSTS" ]; then
        MISSING_VARS+=("ALLOWED_HOSTS")
    fi
    
    if [ ${#MISSING_VARS[@]} -gt 0 ]; then
        echo "❌ 필수 환경 변수가 설정되지 않았습니다: ${MISSING_VARS[*]}"
        echo "⚠️  .env 파일을 확인하고 필수 환경 변수를 설정하세요."
    else
        echo "✅ 필수 환경 변수 확인 완료"
        echo "  - DB_NAME: ${DB_NAME}"
        echo "  - DB_USER: ${DB_USER}"
        echo "  - DB_HOST: ${DB_HOST:-localhost}"
        echo "  - DB_PORT: ${DB_PORT:-3306}"
        echo "  - SECRET_KEY: 설정됨"
        echo "  - ALLOWED_HOSTS: ${ALLOWED_HOSTS}"
    fi
fi

# Django static files 수집
echo "================================"
echo "Django static files 수집 중..."
echo "================================"

# 설정 확인 (디버깅)
echo "Static files 설정 확인 중..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anonymous_project.settings.production')
django.setup()
from django.conf import settings
print(f'USE_S3_STATIC (env): {os.getenv(\"USE_S3_STATIC\")}')
print(f'STATICFILES_STORAGE: {getattr(settings, \"STATICFILES_STORAGE\", \"설정되지 않음\")}')
print(f'STATIC_URL: {settings.STATIC_URL}')
print(f'STATIC_ROOT: {getattr(settings, \"STATIC_ROOT\", \"설정되지 않음\")}')
print(f'AWS_STORAGE_BUCKET_NAME: {getattr(settings, \"AWS_STORAGE_BUCKET_NAME\", \"설정되지 않음\")}')
print(f'AWS_ACCESS_KEY_ID 설정됨: {bool(getattr(settings, \"AWS_ACCESS_KEY_ID\", None))}')
print(f'AWS_SECRET_ACCESS_KEY 설정됨: {bool(getattr(settings, \"AWS_SECRET_ACCESS_KEY\", None))}')
" 2>&1 || echo "⚠️  설정 확인 실패"

# collectstatic 실행 (상세 로그)
echo ""
echo "collectstatic 실행 중..."
# S3 사용 시 상세한 출력을 위해 verbosity를 3으로 설정
VERBOSITY_LEVEL=2
if [ "$USE_S3_STATIC" = "True" ]; then
    VERBOSITY_LEVEL=3
fi

COLLECTSTATIC_OUTPUT=$(python manage.py collectstatic --noinput --clear --verbosity $VERBOSITY_LEVEL 2>&1)
COLLECTSTATIC_EXIT_CODE=$?

echo "$COLLECTSTATIC_OUTPUT"

if [ $COLLECTSTATIC_EXIT_CODE -eq 0 ]; then
    echo "✅ Static files 수집 성공"

    # HTML 캐시 무효화 (새로운 static 파일 URL이 반영되도록)
    echo ""
    echo "HTML 캐시 무효화 중..."
    CACHE_CLEAR_OUTPUT=$(python manage.py shell << EOF 2>&1
from django.core.cache import cache
try:
    cache.clear()
    print("✅ 캐시가 무효화되었습니다.")
except Exception as e:
    print(f"⚠️  캐시 무효화 중 오류 발생: {e}")
    import sys
    sys.exit(1)
EOF
    )
    CACHE_CLEAR_EXIT_CODE=$?
    echo "$CACHE_CLEAR_OUTPUT"
    
    if [ $CACHE_CLEAR_EXIT_CODE -ne 0 ]; then
        echo "⚠️  캐시 무효화 중 오류가 발생했습니다. (계속 진행)"
    fi
    
    # S3 사용 시 업로드 확인
    if [ "$USE_S3_STATIC" = "True" ]; then
        echo ""
        echo "================================"
        echo "S3 업로드 확인 중..."
        echo "================================"
        python -c "
import os
import sys
import django
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anonymous_project.settings.production')
django.setup()

from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

try:
    # AWS 자격 증명 확인
    print('1. AWS 자격 증명 확인 중...')
    if not settings.AWS_ACCESS_KEY_ID:
        print('❌ AWS_ACCESS_KEY_ID가 설정되지 않았습니다.')
        sys.exit(1)
    if not settings.AWS_SECRET_ACCESS_KEY:
        print('❌ AWS_SECRET_ACCESS_KEY가 설정되지 않았습니다.')
        sys.exit(1)
    print(f'   ✅ AWS_ACCESS_KEY_ID: {settings.AWS_ACCESS_KEY_ID[:10]}...')
    print(f'   ✅ AWS_STORAGE_BUCKET_NAME: {settings.AWS_STORAGE_BUCKET_NAME}')
    print(f'   ✅ AWS_S3_REGION_NAME: {getattr(settings, \"AWS_S3_REGION_NAME\", \"ap-northeast-2\")}')
    
    # boto3 클라이언트 생성 및 버킷 접근 확인
    print('')
    print('2. S3 버킷 접근 확인 중...')
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=getattr(settings, 'AWS_S3_REGION_NAME', 'ap-northeast-2')
    )
    
    try:
        s3_client.head_bucket(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
        print(f'   ✅ 버킷 접근 성공: {settings.AWS_STORAGE_BUCKET_NAME}')
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f'   ❌ 버킷을 찾을 수 없습니다: {settings.AWS_STORAGE_BUCKET_NAME}')
        elif error_code == '403':
            print(f'   ❌ 버킷 접근 권한이 없습니다: {settings.AWS_STORAGE_BUCKET_NAME}')
            print(f'   에러: {e}')
        else:
            print(f'   ❌ 버킷 접근 오류: {e}')
        sys.exit(1)
    
    # S3Boto3Storage를 통한 파일 확인
    print('')
    print('3. S3에 업로드된 파일 확인 중...')
    storage = S3Boto3Storage()
    
    # 여러 파일 경로 확인 (다양한 경로 시도)
    test_files = [
        'static/css/style.css',
        'css/style.css',
        'admin/css/base.css',  # Django admin 파일도 확인
        'static/admin/css/base.css',  # Django admin 파일 (static 접두사 포함)
    ]
    
    found_files = []
    not_found_files = []
    
    for file_path in test_files:
        try:
            if storage.exists(file_path):
                found_files.append(file_path)
                print(f'   ✅ 파일 발견: {file_path}')
            else:
                not_found_files.append(file_path)
        except Exception as e:
            print(f'   ⚠️  파일 확인 중 오류 ({file_path}): {e}')
            not_found_files.append(file_path)
    
    # boto3로 직접 확인 (더 정확한 확인)
    print('')
    print('4. boto3로 S3 버킷 내 파일 직접 확인 중...')
    s3_files_found = False
    response = None
    try:
        response = s3_client.list_objects_v2(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Prefix='static/',
            MaxKeys=10
        )
        
        if 'Contents' in response and len(response['Contents']) > 0:
            s3_files_found = True
            print(f'   ✅ S3 버킷에 {len(response[\"Contents\"])}개 이상의 파일이 있습니다.')
            print('   찾은 파일 예시:')
            for obj in response['Contents'][:5]:
                print(f'     - {obj[\"Key\"]} ({obj[\"Size\"]} bytes)')
        else:
            print('   ⚠️  S3 버킷의 static/ 경로에 파일이 없습니다.')
    except Exception as e:
        print(f'   ⚠️  S3 목록 조회 중 오류: {e}')
    
    # 최종 결과
    print('')
    print('================================')
    if found_files or s3_files_found:
        print('✅ S3 업로드 확인 완료')
    else:
        print('⚠️  S3에 파일이 없는 것으로 보입니다.')
        print('   가능한 원인:')
        print('   1. collectstatic이 실제로 S3에 업로드하지 않았을 수 있습니다.')
        print('   2. AWS 자격 증명 또는 버킷 권한 문제')
        print('   3. 파일 경로가 예상과 다를 수 있습니다.')
        print('   디버깅을 위해 collectstatic 출력을 확인하세요.')
    print('================================')
    
except NoCredentialsError:
    print('❌ AWS 자격 증명을 찾을 수 없습니다.')
    print('   AWS_ACCESS_KEY_ID와 AWS_SECRET_ACCESS_KEY를 확인하세요.')
    sys.exit(1)
except Exception as e:
    print(f'❌ S3 확인 중 오류 발생:')
    print(f'   {type(e).__name__}: {e}')
    traceback.print_exc()
    sys.exit(1)
" 2>&1
        S3_CHECK_EXIT_CODE=$?
        
        if [ $S3_CHECK_EXIT_CODE -ne 0 ]; then
            echo ""
            echo "⚠️  S3 확인 중 오류가 발생했습니다. (계속 진행)"
        fi
    fi
else
    echo "❌ Static files 수집 실패"
    echo "에러 상세 내용:"
    python manage.py collectstatic --noinput --clear --verbosity 2 2>&1 | tail -n 30
    echo "⚠️  Static files 수집 실패했지만 계속 진행합니다."
fi

# Django migrations 실행 (상세한 에러 확인)
echo "================================"
echo "데이터베이스 migrations 실행 중..."
echo "================================"

# DB 연결 테스트
echo "DB 연결 테스트 중..."
if python manage.py check --database default 2>&1 | grep -q "System check identified no issues"; then
    echo "✅ Django 시스템 체크 통과"
elif python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anonymous_project.settings.production')
django.setup()
from django.db import connection
connection.ensure_connection()
print('DB 연결 성공')
" 2>&1; then
    echo "✅ DB 연결 확인됨"
else
    echo "⚠️  DB 연결 확인 실패 (migrate 시도는 계속 진행)"
fi

# Migrations 실행
if python manage.py migrate --noinput --verbosity 2; then
    echo "✅ Migrations 실행 성공"
    
    # 생성된 테이블 확인
    echo "================================"
    echo "생성된 테이블 확인 중..."
    python manage.py showmigrations --list | grep -E "^\[X\]|^\[ \]" | head -n 20 || true
    echo "================================"
else
    echo "❌ Migrations 실행 실패"
    echo ""
    echo "================================"
    echo "에러 상세 내용:"
    echo "================================"
    python manage.py migrate --noinput --verbosity 2 2>&1 | tail -n 50
    
    echo ""
    echo "================================"
    echo "디버깅 정보:"
    echo "================================"
    echo "DB 설정 확인:"
    python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anonymous_project.settings.production')
django.setup()
from django.conf import settings
print(f'DB_NAME: {settings.DATABASES[\"default\"][\"NAME\"]}')
print(f'DB_USER: {settings.DATABASES[\"default\"][\"USER\"]}')
print(f'DB_HOST: {settings.DATABASES[\"default\"][\"HOST\"]}')
print(f'DB_PORT: {settings.DATABASES[\"default\"][\"PORT\"]}')
" 2>&1 || echo "DB 설정 확인 실패"
    
    echo ""
    echo "현재 적용된 migrations:"
    python manage.py showmigrations --list | head -n 30 || true
    
    echo ""
    echo "❌ Migrations가 실패했지만 배포는 계속 진행합니다."
    echo "⚠️  애플리케이션이 실행 중 에러가 발생할 수 있습니다."
    echo "⚠️  수동으로 migrate를 실행하세요:"
    echo "   cd $APP_DIR"
    echo "   source $VENV_DIR/bin/activate"
    echo "   export DJANGO_SETTINGS_MODULE=anonymous_project.settings.production"
    echo "   python manage.py migrate"
fi

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

