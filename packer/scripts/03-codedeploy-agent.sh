#!/bin/bash
set -e

echo "================================"
echo "[3/8] AWS CodeDeploy Agent 설치"
echo "================================"

# CodeDeploy Agent 설치 디렉토리
CODEDEPLOY_HOME="/opt/codedeploy-agent"

# 이미 설치되어 있으면 스킵
if [ -d "$CODEDEPLOY_HOME" ]; then
    echo "⚠️  CodeDeploy Agent가 이미 설치되어 있습니다."
    exit 0
fi

# Ruby 설치 (CodeDeploy Agent는 Ruby로 작성됨)
# 참고: apt-get update는 01-base-setup.sh에서 이미 실행됨
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
    ruby \
    ruby-dev \
    wget

# CodeDeploy Agent 다운로드 및 설치
# 참고: Private Subnet에서는 S3 VPC Endpoint 또는 NAT Gateway를 통해 접근해야 함
CODEDEPLOY_REGION="ap-northeast-2"  # 리전에 맞게 변경
cd /home/ubuntu

wget https://aws-codedeploy-${CODEDEPLOY_REGION}.s3.${CODEDEPLOY_REGION}.amazonaws.com/latest/install
chmod +x ./install

# CodeDeploy Agent 설치
sudo ./install auto

# 설치 확인
if sudo service codedeploy-agent status > /dev/null 2>&1; then
    echo "✅ CodeDeploy Agent 설치 완료"
    # 서비스 활성화 및 시작 (AMI에서 enable 상태로 유지, EC2 시작 시 자동 실행)
    sudo systemctl enable codedeploy-agent
    sudo systemctl start codedeploy-agent || true
    echo "✅ CodeDeploy Agent 서비스 활성화 및 시작 완료"
else
    echo "⚠️  CodeDeploy Agent 설치 확인 필요"
    # 설치 실패해도 서비스는 활성화 시도
    sudo systemctl enable codedeploy-agent || true
fi

# 설치 파일 정리
rm -f ./install

echo "✅ CodeDeploy Agent 설치 스크립트 완료"
echo "✅ CodeDeploy Agent가 enable 상태로 설정되어 EC2 시작 시 자동 실행됩니다."

