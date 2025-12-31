#!/bin/bash
set -e

echo "================================"
echo "[5/8] MariaDB Client 설치"
echo "================================"

# 패키지 목록 업데이트
sudo DEBIAN_FRONTEND=noninteractive apt-get update -y

# MariaDB Client 설치 (RDS MariaDB 접속용)
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
    mariadb-client \
    libmariadb-dev \
    libmariadb-dev-compat

# MariaDB Client 버전 확인
mariadb --version || mysql --version

echo "✅ MariaDB Client 설치 완료"
echo "⚠️  참고: RDS 또는 외부 MariaDB 서버에 접속하려면 보안 그룹 설정이 필요합니다."

