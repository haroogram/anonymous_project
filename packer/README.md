# Packer AMI 빌드 가이드

이 디렉토리는 Private Subnet에 배포할 EC2 인스턴스를 위한 커스텀 AMI를 생성하는 Packer 설정을 포함합니다.

## 자동 빌드 (GitHub Actions)

**권장 방법**: GitHub Actions를 사용하여 자동으로 AMI를 빌드할 수 있습니다.

- 워크플로우: `.github/workflows/build-ami.yml`
- 자동 실행: `packer/**` 또는 `requirements.txt` 변경 시
- 수동 실행: GitHub Actions 탭에서 "Build AMI with Packer" 워크플로우 실행
- AMI ID 저장: Systems Manager Parameter Store (`/anonymous-project/ami-id`)

자세한 내용은 `.github/workflows/README.md`를 참조하세요.

---

## 수동 빌드 (로컬)

## 사전 준비

### 1. Packer 설치

#### Windows
```powershell
# Chocolatey 사용
choco install packer

# 또는 직접 다운로드
# https://www.packer.io/downloads
```

#### Linux/Mac
```bash
# Homebrew (Mac)
brew install packer

# 또는 직접 다운로드
# https://www.packer.io/downloads
```

### 2. AWS 자격 증명 설정

AWS CLI가 설치되어 있고 자격 증명이 설정되어 있어야 합니다:

```bash
aws configure
```

또는 환경 변수:
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="ap-northeast-2"
```

### 3. IAM 권한

Packer를 실행하는 사용자/역할은 다음 권한이 필요합니다:

- `ec2:CreateImage`
- `ec2:CopyImage`
- `ec2:RegisterImage`
- `ec2:DescribeImages`
- `ec2:DescribeSnapshots`
- `ec2:DescribeInstances`
- `ec2:RunInstances`
- `ec2:TerminateInstances`
- `ec2:StopInstances`
- `ec2:StartInstances`
- `ec2:CreateTags`
- `ec2:DeleteTags`
- `ec2:CreateSnapshot`
- `ec2:DeleteSnapshot`

### 4. VPC 및 네트워크 설정

**중요**: Private Subnet에서 빌드하려면 다음 중 하나가 필요합니다:

#### 옵션 A: NAT Gateway 사용 (권장)
- Private Subnet이 NAT Gateway를 통해 인터넷 접근 가능해야 함
- VPC에 Internet Gateway와 NAT Gateway가 설정되어 있어야 함

#### 옵션 B: VPC Endpoints 사용
- S3 VPC Endpoint 생성 (CodeDeploy Agent 다운로드용)
- Systems Manager VPC Endpoint (선택사항)

#### 옵션 C: Bastion Host 사용
- Public Subnet에 Bastion Host 생성
- Packer가 SSH로 Bastion을 통해 Private Subnet의 인스턴스에 접근

## 사용 방법

### 1. 변수 설정 파일 생성

```bash
cp packer/variables.pkr.hcl.example packer/variables.pkr.hcl
```

`packer/variables.pkr.hcl` 파일을 열어 실제 값으로 수정:

```hcl
aws_region = "ap-northeast-2"
vpc_id     = "vpc-12345678"
subnet_id  = "subnet-87654321"
source_ami_id = "ami-0c9c942bd7bf113a2"  # Ubuntu 22.04 LTS
instance_type  = "t3.micro"
```

### 2. Packer 검증

```bash
packer validate -var-file=packer/variables.pkr.hcl packer.pkr.hcl
```

### 3. AMI 빌드

```bash
packer build -var-file=packer/variables.pkr.hcl packer.pkr.hcl
```

또는 변수를 직접 지정:

```bash
packer build \
  -var 'vpc_id=vpc-12345678' \
  -var 'subnet_id=subnet-87654321' \
  -var 'aws_region=ap-northeast-2' \
  -var 'source_ami_id=ami-0c9c942bd7bf113a2' \
  packer.pkr.hcl
```

### 4. 빌드된 AMI 확인

빌드가 완료되면 AMI ID가 출력됩니다:
```
==> Builds finished. The artifacts of successful builds are:
--> amazon-ebs.anonymous_project: AMIs were created:
ap-northeast-2: ami-xxxxxxxxxxxxxxxxx
```

AWS Console > EC2 > AMIs에서 생성된 AMI를 확인할 수 있습니다.

## AMI에 포함된 소프트웨어

빌드된 AMI에는 다음이 포함됩니다:

1. ✅ **시스템 업데이트**: 최신 보안 패치
2. ✅ **Python 3**: Python 3.10+ 및 pip, venv
3. ✅ **CodeDeploy Agent**: AWS CodeDeploy 에이전트
4. ✅ **Nginx**: 웹 서버 (설정 파일 포함)
5. ✅ **MariaDB Client**: RDS MariaDB 접속용
6. ✅ **Supervisor**: 프로세스 관리 도구
7. ✅ **기본 유틸리티**: curl, wget, git, vim 등

## 주의사항

### Private Subnet에서의 인터넷 접근

Private Subnet에서 AMI를 빌드할 때는 다음을 확인하세요:

1. **NAT Gateway 설정**: Private Subnet의 라우팅 테이블에 NAT Gateway가 설정되어 있어야 합니다.
2. **보안 그룹**: Packer 빌드 인스턴스에서 인터넷 접근을 허용해야 합니다.
3. **VPC Endpoints**: NAT Gateway 없이 사용하려면 S3 VPC Endpoint가 필요합니다.

### CodeDeploy Agent 설치

CodeDeploy Agent는 S3에서 다운로드되므로:
- S3 VPC Endpoint가 설정되어 있거나
- NAT Gateway를 통해 S3 접근이 가능해야 합니다.

### IAM Instance Profile

`packer.pkr.hcl`에서 `iam_instance_profile`을 실제 Role 이름으로 변경하세요:

```hcl
iam_instance_profile = "your-packer-build-role"
```

이 Role은 다음 권한이 필요합니다:
- S3 읽기 (CodeDeploy Agent 다운로드용)
- EC2 기본 권한

## 문제 해결

### 빌드 실패: "No route to host"
- NAT Gateway 또는 VPC Endpoint 설정 확인
- 보안 그룹에서 아웃바운드 규칙 확인

### CodeDeploy Agent 설치 실패
- S3 접근 권한 확인
- 리전별 CodeDeploy Agent URL 확인:
  - ap-northeast-2: `https://aws-codedeploy-ap-northeast-2.s3.ap-northeast-2.amazonaws.com/latest/install`

### SSH 접근 불가
- Security Group에서 SSH(22) 포트 허용 확인
- VPC CIDR 블록이 `temporary_security_group_source_cidr`에 포함되어 있는지 확인

## 다음 단계

AMI 빌드 후:

1. EC2 인스턴스 생성 시 생성된 AMI 선택
2. Private Subnet에 인스턴스 배치
3. CodeDeploy Agent 시작:
   ```bash
   sudo systemctl start codedeploy-agent
   sudo systemctl enable codedeploy-agent
   ```
4. CodeDeploy 애플리케이션 및 배포 그룹 설정
5. 배포 실행

자세한 배포 가이드는 프로젝트 루트의 `README.md`를 참조하세요.

