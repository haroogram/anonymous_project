#!/bin/bash
# Ubuntu 22.04 LTS 환경용 기본 시스템 패키지 설치 스크립트
# set -e는 일시적으로 해제 (오류 처리를 위해)
set +e

# Ubuntu/Debian 계열 시스템에서 비대화형 모드 설정
# DEBIAN_FRONTEND는 Ubuntu에서도 정상 작동 (Ubuntu는 Debian 기반)
export DEBIAN_FRONTEND=noninteractive

echo "================================"
echo "[1/8] 기본 시스템 패키지 설치"
echo "================================"

# 시스템 업데이트 (패키지 목록 갱신 필수)
echo "패키지 목록 업데이트 중..."
sudo apt-get update -y
UPDATE_RESULT=$?

if [ $UPDATE_RESULT -ne 0 ]; then
    echo "⚠️ 패키지 목록 업데이트 실패, 재시도 중..."
    sleep 3
    sudo apt-get update -y
    if [ $? -ne 0 ]; then
        echo "❌ 패키지 목록 업데이트 실패"
        exit 1
    fi
fi

# 참고: apt-get upgrade는 제거 (AMI 빌드 시 베이스 이미지가 최신이므로 불필요하고 시간 소요)

echo "필수 패키지 설치 중..."
# 필수 패키지 설치 (build-essential 포함)
sudo apt-get install -y \
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

INSTALL_RESULT=$?

# build-essential 설치 실패 시에만 재시도 (이미 설치되어 있으면 스킵)
if [ $INSTALL_RESULT -ne 0 ]; then
    if ! dpkg -l | grep -q "^ii.*build-essential"; then
        echo "⚠️ 패키지 설치 실패, build-essential 재시도 중..."
        # 재시도 시에만 update 실행 (중복 방지)
        sudo apt-get update -y
        sudo apt-get install -y build-essential || {
            echo "❌ build-essential 설치 실패"
            echo "사용 가능한 패키지 확인 중..."
            apt-cache search build-essential || true
            exit 1
        }
    fi
fi

# set -e 다시 활성화
set -e

# 타임존 설정 (Asia/Seoul)
sudo timedatectl set-timezone Asia/Seoul

# 로케일 설정
sudo locale-gen ko_KR.UTF-8
sudo update-locale LANG=ko_KR.UTF-8

echo "✅ 기본 시스템 패키지 설치 완료"
echo "⚠️  참고: 패키지 정리는 08-cleanup.sh에서 수행됩니다."

