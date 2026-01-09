#!/bin/bash
# Ubuntu 22.04 LTS 환경용 Python 3 및 pip 설치 스크립트
set -e

# Ubuntu/Debian 계열 시스템에서 비대화형 모드 설정
export DEBIAN_FRONTEND=noninteractive

echo "================================"
echo "[2/8] Python 3 및 pip 설치"
echo "================================"

# Python 3.12 설치 (Ubuntu 22.04는 기본적으로 3.10이지만 최신 버전 설치)
# 참고: apt-get update는 01-base-setup.sh에서 이미 실행됨
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-setuptools \
    python3-wheel

# pip 업그레이드 (setuptools는 81 미만으로 고정)
sudo python3 -m pip install --upgrade pip wheel
sudo python3 -m pip install "setuptools<81"

# Python 버전 확인
python3 --version
pip3 --version

echo "✅ Python 3 설치 완료"
echo "⚠️  참고: gunicorn은 requirements.txt를 통해 가상환경에 설치됩니다 (02-5-python-packages.sh)."

