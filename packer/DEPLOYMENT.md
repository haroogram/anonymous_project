# Private Subnet 배포 가이드

Private Subnet에 배포하기 위한 전체 워크플로우입니다.

## 아키텍처 개요

```
Internet Gateway
      |
   [NAT Gateway] <-- Public Subnet
      |
   [Private Subnet] <-- EC2 인스턴스 (애플리케이션)
      |
   [Private Subnet] <-- RDS (MariaDB)
```

또는 VPC Endpoints 사용:

```
Internet Gateway
      |
   [VPC Endpoints] <-- S3, CodeDeploy 등
      |
   [Private Subnet] <-- EC2 인스턴스
```

## 사전 준비

### 1. VPC 구성

- [x] VPC 생성
- [x] Public Subnet 생성 (NAT Gateway용)
- [x] Private Subnet 생성 (EC2용)
- [x] Internet Gateway 연결
- [x] NAT Gateway 생성 (Public Subnet에)
- [x] 라우팅 테이블 설정:
  - Public Subnet: 0.0.0.0/0 → Internet Gateway
  - Private Subnet: 0.0.0.0/0 → NAT Gateway

### 2. 보안 그룹 설정

**EC2 보안 그룹 (Private Subnet)**
- 인바운드:
  - SSH (22): VPC CIDR 또는 Bastion Host IP
  - HTTP (80): ALB/Public Subnet CIDR
  - HTTPS (443): ALB/Public Subnet CIDR
- 아웃바운드:
  - 모든 트래픽 허용 (NAT Gateway 통해)

**RDS 보안 그룹**
- 인바운드:
  - MariaDB (3306): EC2 보안 그룹만 허용

### 3. IAM 역할 생성

**EC2 Instance Profile용 역할** (생성된 AMI에서 사용)

필요한 권한:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::your-codedeploy-bucket/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "codedeploy:PutLifecycleEventHookExecutionStatus"
      ],
      "Resource": "*"
    }
  ]
}
```

## 단계별 배포 절차

### Step 1: Packer로 AMI 빌드

```bash
# 1. 변수 설정
cp packer/variables.pkr.hcl.example packer/variables.pkr.hcl
# packer/variables.pkr.hcl 편집

# 2. AMI 빌드
packer build -var-file=packer/variables.pkr.hcl packer.pkr.hcl

# 3. 생성된 AMI ID 확인
# 출력 예시: ap-northeast-2: ami-xxxxxxxxxxxxxxxxx
```

### Step 2: EC2 인스턴스 생성

1. **AMI 선택**: Step 1에서 생성한 AMI 선택
2. **인스턴스 타입**: t3.small 이상 권장
3. **네트워크 설정**:
   - VPC: Private Subnet이 속한 VPC
   - Subnet: Private Subnet
   - Auto-assign Public IP: Disable
4. **IAM 역할**: 위에서 생성한 EC2 Instance Profile 역할 선택
5. **보안 그룹**: EC2 보안 그룹 선택
6. **스토리지**: 20GB 이상 권장

### Step 3: EC2 인스턴스 초기 설정

SSH 접근 (Bastion Host 통하거나 Systems Manager Session Manager 사용):

```bash
# SSH (Bastion Host 통한 접근)
ssh -J ubuntu@bastion-host ubuntu@private-ec2-ip

# 또는 Systems Manager Session Manager
aws ssm start-session --target i-xxxxxxxxxxxxx
```

초기 설정:

```bash
# 1. CodeDeploy Agent 시작
sudo systemctl start codedeploy-agent
sudo systemctl enable codedeploy-agent
sudo systemctl status codedeploy-agent

# 2. 환경 변수 파일 생성
sudo nano /home/ubuntu/app/.env

# .env 내용:
# SECRET_KEY=your-production-secret-key
# DEBUG=False
# ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
# DJANGO_SETTINGS_MODULE=anonymous_project.settings.production
# DB_NAME=anonymous_db
# DB_USER=db_user
# DB_PASSWORD=your_secure_password
# DB_HOST=rds-endpoint.region.rds.amazonaws.com
# DB_PORT=3306

# 3. 파일 권한 설정
sudo chown -R ubuntu:ubuntu /home/ubuntu/app
```

### Step 4: RDS (MariaDB) 설정

1. **RDS 인스턴스 생성**:
   - 엔진: MariaDB
   - VPC: 동일 VPC
   - Subnet: Private Subnet
   - 보안 그룹: EC2 보안 그룹 허용

2. **데이터베이스 생성**:
   ```sql
   CREATE DATABASE anonymous_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'db_user'@'%' IDENTIFIED BY 'your_secure_password';
   GRANT ALL PRIVILEGES ON anonymous_db.* TO 'db_user'@'%';
   FLUSH PRIVILEGES;
   ```

### Step 5: CodeDeploy 설정

1. **CodeDeploy 애플리케이션 생성**
2. **배포 그룹 생성**:
   - 배포 유형: In-place
   - 환경 구성: EC2 인스턴스
   - 태그 또는 인스턴스 직접 선택
3. **서비스 역할**: CodeDeploy 서비스 역할 생성 및 연결

### Step 6: 첫 배포

```bash
# 로컬에서 (또는 CI/CD에서)
aws deploy create-deployment \
  --application-name anonymous-project \
  --deployment-group-name production \
  --s3-location bucket=your-codedeploy-bucket,bundleType=zip,key=deploy.zip

# 또는 AWS Console에서 수동 배포
```

### Step 7: Nginx 및 Supervisor 설정

EC2 인스턴스에서:

```bash
# Nginx 설정 확인 및 시작
sudo nginx -t
sudo systemctl start nginx
sudo systemctl enable nginx

# Supervisor 설정 확인
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start anonymous_project

# 상태 확인
sudo supervisorctl status
sudo systemctl status nginx
```

## 문제 해결

### CodeDeploy Agent가 시작되지 않음

```bash
# 로그 확인
sudo tail -f /var/log/aws/codedeploy-agent/codedeploy-agent.log

# IAM 역할 확인
aws sts get-caller-identity  # EC2에서 실행

# S3 접근 확인
aws s3 ls s3://your-codedeploy-bucket
```

### RDS 연결 실패

```bash
# EC2에서 RDS 연결 테스트
mysql -h rds-endpoint -u db_user -p

# 보안 그룹 확인:
# - RDS 보안 그룹에서 EC2 보안 그룹 허용
# - 포트 3306 열려있는지 확인
```

### 인터넷 접근 불가 (NAT Gateway 문제)

```bash
# 라우팅 테이블 확인
aws ec2 describe-route-tables --filters "Name=vpc-id,Values=vpc-xxx"

# NAT Gateway 상태 확인
aws ec2 describe-nat-gateways --filter "Name=vpc-id,Values=vpc-xxx"
```

## 보안 체크리스트

- [ ] Private Subnet에 Public IP 할당 안 함
- [ ] 보안 그룹 최소 권한 원칙 적용
- [ ] RDS는 Private Subnet에만 배치
- [ ] IAM 역할 최소 권한 적용
- [ ] Secrets Manager 또는 Parameter Store로 민감 정보 관리
- [ ] VPC Flow Logs 활성화 (감사 목적)

## 비용 최적화

- NAT Gateway: 시간당 비용 발생 → VPC Endpoints 고려
- RDS: 인스턴스 타입 선택 시 비용 고려
- EC2: 필요한 만큼만 사용, Auto Scaling 고려

## 다음 단계

- [ ] ALB(Application Load Balancer) 추가
- [ ] Auto Scaling 그룹 설정
- [ ] CloudWatch 모니터링 설정
- [ ] 백업 전략 수립

