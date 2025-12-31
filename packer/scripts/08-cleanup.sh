#!/bin/bash
set -e

echo "================================"
echo "[8/8] 정리 및 최적화"
echo "================================"

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

