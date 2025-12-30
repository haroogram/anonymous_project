#!/bin/bash

# anonymous 프로젝트 자동 환경 설정 스크립트
# 사용법: ./setup.sh

set -e  # 에러 발생 시 스크립트 중단

echo "=========================================="
echo "anonymous 프로젝트 환경 설정을 시작합니다"
echo "=========================================="

# 1. Python 버전 확인 및 설치
echo ""
echo "[1/7] Python 버전 확인 중..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3가 설치되어 있지 않습니다."
    echo ""
    echo "Python3를 자동으로 설치하려고 시도합니다..."
    echo ""
    
    # OS 감지 및 Python 설치 시도
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux 배포판 감지
        if command -v apt-get &> /dev/null; then
            # Ubuntu/Debian
            echo "Ubuntu/Debian 시스템을 감지했습니다."
            read -p "Python3를 설치하시겠습니까? (sudo 권한 필요) [y/N]: " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                set +e  # 일시적으로 에러 처리 비활성화
                sudo apt-get update
                sudo apt-get install -y python3 python3-pip python3-venv
                INSTALL_RESULT=$?
                set -e  # 에러 처리 다시 활성화
                if [ $INSTALL_RESULT -ne 0 ]; then
                    echo "❌ Python3 설치에 실패했습니다. sudo 권한을 확인해주세요."
                    exit 1
                fi
                echo "✅ Python3 설치 완료"
            else
                echo "❌ Python3 설치가 취소되었습니다."
                echo ""
                echo "수동 설치 방법:"
                echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-venv"
                echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
                echo "  macOS: brew install python3"
                exit 1
            fi
        elif command -v yum &> /dev/null; then
            # CentOS/RHEL
            echo "CentOS/RHEL 시스템을 감지했습니다."
            read -p "Python3를 설치하시겠습니까? (sudo 권한 필요) [y/N]: " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                set +e  # 일시적으로 에러 처리 비활성화
                sudo yum install -y python3 python3-pip
                INSTALL_RESULT=$?
                set -e  # 에러 처리 다시 활성화
                if [ $INSTALL_RESULT -ne 0 ]; then
                    echo "❌ Python3 설치에 실패했습니다. sudo 권한을 확인해주세요."
                    exit 1
                fi
                echo "✅ Python3 설치 완료"
            else
                echo "❌ Python3 설치가 취소되었습니다."
                echo ""
                echo "수동 설치 방법: sudo yum install python3 python3-pip"
                exit 1
            fi
        else
            echo "❌ 지원되지 않는 Linux 배포판입니다."
            echo "Python3를 수동으로 설치해주세요."
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        echo "macOS 시스템을 감지했습니다."
        if command -v brew &> /dev/null; then
            read -p "Homebrew를 사용하여 Python3를 설치하시겠습니까? [y/N]: " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                set +e  # 일시적으로 에러 처리 비활성화
                brew install python3
                INSTALL_RESULT=$?
                set -e  # 에러 처리 다시 활성화
                if [ $INSTALL_RESULT -ne 0 ]; then
                    echo "❌ Python3 설치에 실패했습니다."
                    exit 1
                fi
                echo "✅ Python3 설치 완료"
            else
                echo "❌ Python3 설치가 취소되었습니다."
                echo ""
                echo "수동 설치 방법: brew install python3"
                exit 1
            fi
        else
            echo "❌ Homebrew가 설치되어 있지 않습니다."
            echo ""
            echo "Python3를 설치하는 방법:"
            echo "  1. Homebrew 설치: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            echo "  2. Python3 설치: brew install python3"
            echo "  또는 Python 공식 사이트에서 다운로드: https://www.python.org/downloads/"
            exit 1
        fi
    else
        echo "❌ 지원되지 않는 운영체제입니다."
        echo "Python3를 수동으로 설치해주세요: https://www.python.org/downloads/"
        exit 1
    fi
fi

PYTHON_VERSION=$(python3 --version)
echo "✅ $PYTHON_VERSION 확인됨"

# 2. 가상환경 생성
echo ""
echo "[2/7] 가상환경 생성 중..."
if [ -d "venv" ]; then
    echo "⚠️  venv 폴더가 이미 존재합니다. 기존 가상환경을 사용합니다."
else
    python3 -m venv venv
    echo "✅ 가상환경 생성 완료"
fi

# 3. 가상환경 활성화 및 의존성 설치
echo ""
echo "[3/7] 가상환경 활성화 및 의존성 설치 중..."
source venv/bin/activate

# pip 업그레이드
pip install --upgrade pip --quiet

# requirements.txt 설치
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ 의존성 설치 완료"
else
    echo "❌ requirements.txt 파일을 찾을 수 없습니다."
    exit 1
fi

# 4. .env 파일 생성
echo ""
echo "[4/7] 환경 변수 파일 설정 중..."
if [ -f ".env" ]; then
    echo "⚠️  .env 파일이 이미 존재합니다. 기존 파일을 유지합니다."
else
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ .env 파일 생성 완료 (.env.example을 복사했습니다)"
        echo "   필요시 .env 파일을 수정하여 환경 변수를 설정하세요."
    else
        echo "⚠️  .env.example 파일이 없습니다. 기본 .env 파일을 생성합니다."
        cat > .env << EOF
# Django Settings
SECRET_KEY=django-insecure-dev-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database 설정 (선택사항)
# MariaDB 사용 시 아래 주석을 해제하고 설정하세요
# DB_ENGINE=mysql
# DB_NAME=anonymous_db
# DB_USER=root
# DB_PASSWORD=your_password
# DB_HOST=localhost
# DB_PORT=3306
EOF
        echo "✅ 기본 .env 파일 생성 완료"
    fi
fi

# 5. 데이터베이스 마이그레이션
echo ""
echo "[5/7] 데이터베이스 마이그레이션 실행 중..."
python manage.py makemigrations
python manage.py migrate --noinput
echo "✅ 데이터베이스 마이그레이션 완료"

# 6. 정적 파일 수집 (선택사항)
echo ""
echo "[6/7] 정적 파일 수집 중..."
python manage.py collectstatic --noinput --clear || echo "⚠️  정적 파일 수집 중 오류 발생 (개발 환경에서는 무시 가능)"
echo "✅ 정적 파일 수집 완료"

echo ""
echo "=========================================="
echo "✅ 환경 설정이 완료되었습니다!"
echo "=========================================="
echo ""
echo "다음 명령어로 개발 서버를 실행할 수 있습니다:"
echo ""
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "또는 다음 명령어로 슈퍼유저를 생성할 수 있습니다:"
echo ""
echo "  python manage.py createsuperuser"
echo ""
echo "=========================================="

