#!/bin/bash
set -e

echo "================================"
echo "[8/8] 정리 및 최적화"
echo "================================"

# Nginx 설정 파일 정리 (이전 설정 제거)
echo "Nginx 설정 파일 정리 중..."
# sites-enabled 하위의 모든 심볼릭 링크 제거 (이전 설정 제거)
sudo rm -f /etc/nginx/sites-enabled/* 2>/dev/null || true
# sites-available 하위의 이전 설정 파일 제거 (anonymous_project 제외)
sudo find /etc/nginx/sites-available/ -type f ! -name "anonymous_project" ! -name "default" ! -name "default.backup" -delete 2>/dev/null || true
# anonymous_project 설정 파일도 제거 (04-nginx-setup.sh에서 새로 생성됨)
sudo rm -f /etc/nginx/sites-available/anonymous_project 2>/dev/null || true
echo "✅ Nginx 설정 파일 정리 완료"

# APT 캐시 정리
sudo apt-get autoremove -y
sudo apt-get autoclean -y
sudo apt-get clean -y

# 로그 파일 정리
sudo truncate -s 0 /var/log/*.log 2>/dev/null || true
sudo truncate -s 0 /var/log/**/*.log 2>/dev/null || true

# 임시 파일 정리
sudo rm -rf /tmp/*
sudo rm -rf /var/tmp/*

# SSH 호스트 키 제거 (보안상 인스턴스별로 새로운 키 생성)
sudo rm -f /etc/ssh/ssh_host_*

# 히스토리 정리
sudo truncate -s 0 ~/.bash_history
sudo rm -f ~/.bash_history

# 루트 히스토리 정리
sudo truncate -s 0 /root/.bash_history 2>/dev/null || true
sudo rm -f /root/.bash_history 2>/dev/null || true

# 패키지 관리자 락 파일 정리
sudo rm -f /var/lib/apt/lists/lock
sudo rm -f /var/cache/apt/archives/lock
sudo rm -f /var/lib/dpkg/lock*

echo "✅ 정리 및 최적화 완료"

