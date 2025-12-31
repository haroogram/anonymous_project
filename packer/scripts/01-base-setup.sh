#!/bin/bash
set -e

echo "================================"
echo "[1/8] 기본 시스템 패키지 설치"
echo "================================"

# 시스템 업데이트
sudo DEBIAN_FRONTEND=noninteractive apt-get update -y
sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y

# 필수 패키지 설치
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
    curl \
    wget \
    git \
    unzip \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    ufw \
    htop \
    vim \
    nano \
    net-tools \
    tzdata

# 타임존 설정 (Asia/Seoul)
sudo timedatectl set-timezone Asia/Seoul

# 로케일 설정
sudo locale-gen ko_KR.UTF-8
sudo update-locale LANG=ko_KR.UTF-8

# 불필요한 패키지 정리
sudo apt-get autoremove -y
sudo apt-get autoclean -y

echo "✅ 기본 시스템 패키지 설치 완료"

