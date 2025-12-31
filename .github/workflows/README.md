# GitHub Actions 워크플로우 가이드

이 디렉토리에는 프로젝트의 CI/CD 워크플로우가 포함되어 있습니다.

## 워크플로우 목록

### 1. `build-ami.yml` - AMI 빌드

**목적**: Packer를 사용하여 커스텀 AMI 생성

**트리거**:
- 수동 실행 (`workflow_dispatch`)
- `packer/**`, `packer.pkr.hcl`, `requirements.txt` 변경 시
- 매월 1일 자정 자동 실행 (보안 업데이트 반영)

**주요 작업**:
1. Packer 설치
2. Packer 설정 검증
3. AMI 빌드 (10-15분 소요)
4. AMI ID를 Systems Manager Parameter Store에 저장
5. AMI에 태그 추가

**필요한 GitHub Secrets**:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

**필요한 AWS 권한**:
- EC2: CreateImage, DescribeImages, CreateTags
- Systems Manager: PutParameter, GetParameter

**결과**:
- 생성된 AMI ID는 `/anonymous-project/ami-id` Parameter Store에 저장됨
- 다음 배포에서 이 AMI를 사용할 수 있음

### 2. `deploy.yml` - 애플리케이션 배포

**목적**: CodeDeploy를 사용하여 애플리케이션 코드 배포

**트리거**:
- `main` 브랜치에 push
- 수동 실행 (`workflow_dispatch`)

**주요 작업**:
1. 배포 패키지 생성 (zip)
2. S3에 업로드
3. CodeDeploy 배포 생성
4. 배포 완료 대기

**필요한 GitHub Secrets**:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `S3_BUCKET` (CodeDeploy 배포 파일 저장용)
- `CODE_DEPLOY_APPLICATION` (CodeDeploy 애플리케이션 이름)
- `CODE_DEPLOY_DEPLOYMENT_GROUP` (배포 그룹 이름)

## 워크플로우 사용 시나리오

### 시나리오 1: 인프라 변경 (Python 버전 업그레이드 등)

```bash
# 1. packer/scripts/02-python-setup.sh 수정
# 2. 커밋 및 푸시
git add packer/scripts/02-python-setup.sh
git commit -m "Update Python version"
git push origin main

# 3. build-ami.yml 자동 실행
# 4. 새 AMI 생성 완료 후 EC2 인스턴스 교체
```

### 시나리오 2: 애플리케이션 코드 변경

```bash
# 1. 코드 수정
# 2. 커밋 및 푸시
git add .
git commit -m "Add new feature"
git push origin main

# 3. deploy.yml 자동 실행
# 4. CodeDeploy로 배포 완료
```

### 시나리오 3: 수동 AMI 빌드

1. GitHub Actions 탭으로 이동
2. "Build AMI with Packer" 워크플로우 선택
3. "Run workflow" 클릭
4. 필요시 "Force rebuild" 옵션 선택

## AMI ID 사용하기

빌드된 AMI ID는 Systems Manager Parameter Store에 저장됩니다:

```bash
# AMI ID 조회
aws ssm get-parameter \
  --name "/anonymous-project/ami-id" \
  --query 'Parameter.Value' \
  --output text

# EC2 인스턴스 생성 시 사용
aws ec2 run-instances \
  --image-id $(aws ssm get-parameter --name "/anonymous-project/ami-id" --query 'Parameter.Value' --output text) \
  --instance-type t3.small \
  --subnet-id subnet-private-xxx \
  ...
```

## 문제 해결

### AMI 빌드 실패

1. `packer/variables.pkr.hcl` 파일 확인
2. VPC, Subnet ID가 올바른지 확인
3. Public Subnet이 인터넷 접근 가능한지 확인
4. IAM 권한 확인

### 배포 실패

1. CodeDeploy Agent가 EC2에서 실행 중인지 확인
2. S3 버킷 접근 권한 확인
3. CodeDeploy 애플리케이션/배포 그룹 이름 확인

## 보안 고려사항

- GitHub Secrets에 민감 정보 저장
- IAM 역할에 최소 권한 원칙 적용
- AMI 빌드 시 임시 보안 그룹 사용 (자동 삭제)
- 배포 패키지에 `.env` 파일 제외 확인

