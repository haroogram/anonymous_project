#!/bin/bash
set -e

echo "================================"
echo "[2.5/8] Python 패키지 사전 설치"
echo "================================"

# requirements.txt가 있는지 확인
if [ ! -f "/tmp/requirements.txt" ]; then
    echo "⚠️  requirements.txt를 찾을 수 없습니다. 스킵합니다."
    exit 0
fi

# Python 가상환경 생성 (AMI에 미리 설치해두기)
VENV_DIR="/home/ubuntu/venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Python 가상환경 생성 중..."
    python3 -m venv $VENV_DIR
    sudo chown -R ubuntu:ubuntu $VENV_DIR
fi

# 가상환경 활성화
echo "가상환경 활성화 및 패키지 설치 중..."
source $VENV_DIR/bin/activate

# pip 업그레이드
pip install --upgrade pip setuptools wheel

# requirements.txt의 패키지들 설치 (AMI 빌드 시점에 인터넷 접근 가능)
echo "requirements.txt 패키지 설치 중..."
pip install -r /tmp/requirements.txt

# 설치된 패키지 목록 저장 (디버깅용)
pip freeze > /tmp/installed_packages.txt
echo "설치된 패키지 목록:"
cat /tmp/installed_packages.txt

# gunicorn 설치 확인 (중요!)
echo ""
echo "gunicorn 설치 확인 중..."
if command -v $VENV_DIR/bin/gunicorn &> /dev/null; then
    echo "✅ gunicorn 설치 확인됨: $($VENV_DIR/bin/gunicorn --version)"
else
    echo "❌ gunicorn을 찾을 수 없습니다!"
    exit 1
fi

# 가상환경 비활성화
deactivate

# requirements.txt를 /home/ubuntu에 복사 (배포 시 사용)
sudo cp /tmp/requirements.txt /home/ubuntu/requirements.txt
sudo chown ubuntu:ubuntu /home/ubuntu/requirements.txt

echo "✅ Python 패키지 사전 설치 완료"
echo "   가상환경 위치: $VENV_DIR"
echo "   설치된 패키지들은 배포 시 재사용됩니다."

