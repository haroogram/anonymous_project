#!/bin/bash
set -e

echo "================================"
echo "[7/8] 디렉토리 구조 생성"
echo "================================"

# 애플리케이션 디렉토리
APP_DIR="/home/ubuntu/anonymous_project"
VENV_DIR="/home/ubuntu/venv"
LOG_DIR="/home/ubuntu/anonymous_project/logs"

# 디렉토리 생성
sudo mkdir -p $APP_DIR
sudo mkdir -p $LOG_DIR
sudo mkdir -p $APP_DIR/staticfiles
sudo mkdir -p $APP_DIR/media

# 권한 설정
sudo chown -R ubuntu:ubuntu $APP_DIR
sudo chown -R ubuntu:ubuntu $VENV_DIR 2>/dev/null || true

# 로그 디렉토리 권한
sudo chmod 755 $LOG_DIR
sudo chmod 755 $APP_DIR/staticfiles
sudo chmod 755 $APP_DIR/media

# Python 가상환경 디렉토리 생성 (나중에 생성될 예정이지만 미리 생성)
sudo mkdir -p $VENV_DIR
sudo chown ubuntu:ubuntu $VENV_DIR

echo "✅ 디렉토리 구조 생성 완료"

