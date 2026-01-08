#!/bin/bash
# Ubuntu 22.04 LTS 환경용 MariaDB Client 설치 스크립트
set -e

# Ubuntu/Debian 계열 시스템에서 비대화형 모드 설정
export DEBIAN_FRONTEND=noninteractive

echo "================================"
echo "[5/8] MariaDB Client 설치"
echo "================================"

# MariaDB Client 설치 (RDS MariaDB 접속용)
# 참고: apt-get update는 01-base-setup.sh에서 이미 실행됨
sudo apt-get install -y \
    mariadb-client \
    libmariadb-dev \
    libmariadb-dev-compat

# MariaDB Client 버전 확인
mariadb --version || mysql --version

echo "✅ MariaDB Client 설치 완료"
echo "⚠️  참고: RDS 또는 외부 MariaDB 서버에 접속하려면 보안 그룹 설정이 필요합니다."

