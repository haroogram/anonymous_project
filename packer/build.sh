#!/bin/bash
# Packer AMI 빌드 스크립트 (Linux/Mac)

set -e

echo "================================"
echo "Packer AMI 빌드 시작"
echo "================================"

# 변수 파일 확인
if [ ! -f "packer/variables.pkr.hcl" ]; then
    echo "❌ variables.pkr.hcl 파일이 없습니다."
    echo "packer/variables.pkr.hcl.example을 복사하여 설정하세요."
    exit 1
fi

# Packer 설치 확인
if ! command -v packer &> /dev/null; then
    echo "❌ Packer가 설치되어 있지 않습니다."
    echo "https://www.packer.io/downloads 에서 설치하세요."
    exit 1
fi

# 스크립트 실행 권한 부여
chmod +x packer/scripts/*.sh

echo ""
echo "[1/3] Packer 설정 검증 중..."
packer validate -var-file=packer/variables.pkr.hcl packer.pkr.hcl

echo ""
echo "[2/3] AMI 빌드 시작..."
echo "이 작업은 10-15분 정도 소요될 수 있습니다."
echo ""

packer build -var-file=packer/variables.pkr.hcl packer.pkr.hcl

if [ $? -eq 0 ]; then
    echo ""
    echo "================================"
    echo "✅ AMI 빌드 완료!"
    echo "================================"
    echo ""
    echo "다음 단계:"
    echo "1. AWS Console > EC2 > AMIs에서 생성된 AMI 확인"
    echo "2. 해당 AMI를 사용하여 EC2 인스턴스 생성"
    echo "3. Private Subnet에 배치"
else
    echo ""
    echo "❌ AMI 빌드 실패"
    exit 1
fi

