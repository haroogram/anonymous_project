#!/bin/bash

# BeforeInstall 스크립트
# 배포 전 준비 작업 수행

set -e  # 에러 발생 시 스크립트 중단

echo "================================"
echo "BeforeInstall 시작"
echo "================================"

# 로그 디렉토리 생성
sudo mkdir -p /home/ubuntu/app/logs
sudo chown -R ubuntu:ubuntu /home/ubuntu/app/logs

# 이전 배포 디렉토리 백업 (선택사항)
if [ -d "/home/ubuntu/app" ]; then
    echo "이전 배포 디렉토리 백업 중..."
    sudo cp -r /home/ubuntu/app /home/ubuntu/app_backup_$(date +%Y%m%d_%H%M%S) || true
fi

# 필요한 시스템 패키지 설치 확인 (필요한 경우)
# sudo apt-get update
# sudo apt-get install -y python3-pip python3-venv nginx

echo "BeforeInstall 완료"

