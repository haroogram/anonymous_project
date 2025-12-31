#!/bin/bash
set -e

echo "================================"
echo "[2/8] Python 3 및 pip 설치"
echo "================================"

# 패키지 목록 업데이트 (필요시)
echo "패키지 목록 확인 중..."
sudo DEBIAN_FRONTEND=noninteractive apt-get update -y || true

# Python 3.12 설치 (Ubuntu 22.04는 기본적으로 3.10이지만 최신 버전 설치)
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-setuptools \
    python3-wheel

# pip 업그레이드
sudo python3 -m pip install --upgrade pip setuptools wheel

# Python 버전 확인
python3 --version
pip3 --version

# 전역 Python 패키지 (필요한 경우만)
# sudo pip3 install --upgrade pip setuptools wheel

echo "✅ Python 3 설치 완료"

