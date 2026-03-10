# GitHub Actions 워크플로우 가이드

이 디렉토리에는 프로젝트의 CI/CD 워크플로우가 포함되어 있습니다.

## 워크플로우 목록

### 1. `docker-build-push.yml` - Docker 이미지 빌드 및 Docker Hub 푸시 (K3s/ArgoCD 배포용)

**목적**: 태그(`v*`) 푸시 시 Docker 이미지를 빌드하고 Docker Hub에 푸시. (선택) dso_project의 K3s manifest를 자동으로 수정해 ArgoCD가 새 이미지를 배포하도록 함.

**트리거**:
- `v*` 태그 push (예: `v1.1.4` → 이미지 태그 `1.1.4` 추가)
- 수동 실행 (`workflow_dispatch`)

**푸시되는 이미지 태그**:
- `sha-<short_sha>` (예: `sha-a1b2c3d`) — 항상
- `latest` — 항상
- `<version>` (예: `1.1.4`) — 태그 push 시에만 (`v1.1.4` 푸시 시)

**필요한 GitHub Secrets**:
- `DOCKERHUB_USERNAME` — Docker Hub 사용자명
- `DOCKERHUB_TOKEN` — Docker Hub Access Token (비밀번호 대신 사용 권장)

**배포 흐름 (태그 기반 배포)**:
1. anonymous_project에서 코드 수정 후 수시로 `branch`에 push (CI 대상, 배포 아님)
2. 배포하고 싶은 시점에 `branch` 최신 커밋 기준으로 버전 태그 생성:
   ```bash
   git checkout 'branch'
   git pull origin 'branch'
   git tag v1.1.4
   git push origin v1.1.4
   ```
3. `v1.1.4` 태그 push 시 본 워크플로가 실행되어 Docker 이미지를 빌드·푸시
4. **(자동)** `DSO_REPO_TOKEN`이 설정되어 있으면, dso_project 레포를 체크아웃해 `k8s-manifests/deployment.yaml`의 image 태그를 새 태그(`1.1.4`)로 갱신 후 push
5. ArgoCD가 dso_project repo를 polling하여 변경 감지 후 K3s에 새 이미지로 배포

**K3s manifest 자동 갱신(선택)**  
dso_project의 manifest까지 CI에서 자동으로 바꿔서 push하려면 다음을 설정한다.

| 구분 | 이름 | 설명 |
|------|------|------|
| Secret | `DSO_REPO_TOKEN` | dso_project 레포에 **push** 권한(content write)이 있는 Personal Access Token (repo 권한) |
| Variable | `DSO_MANIFEST_REPO` | (선택) manifest 레포 전체 이름. 미설정 시 `기본값` 사용 |

- `DSO_REPO_TOKEN`을 비워 두면 **Docker 빌드·푸시만** 하고, manifest 수정 job은 건너뛴다.
- 토큰은 GitHub → Settings → Developer settings → Personal access tokens 에서 생성하고, **repo** 체크 후 사용.

### 2. `build-ami.yml` - AMI 빌드

**목적**: Packer를 사용하여 커스텀 AMI 생성

**트리거**:
- 수동 실행 (`workflow_dispatch`)  
  *(이전에는 매월 1일 자정 자동 실행 스케줄이 있었지만, 현재 워크플로 파일에서는 주석 처리되어 있어 자동 실행되지 않습니다.)*

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

### 3. `deploy.yml` - 애플리케이션 배포

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

### 시나리오 2: 애플리케이션 코드 변경 (K3s/ArgoCD + Docker 이미지 배포)

```bash
# 1. 코드 수정
# 2. 커밋 및 푸시 (CI 용도, 배포 아님)
git add .
git commit -m "Add new feature"
git push origin main

# 3. 배포할 시점에 main 최신 커밋에 태그 생성 후 푸시
git checkout main
git pull origin main
git tag v1.1.4
git push origin v1.1.4

# 4. docker-build-push.yml이 실행되어 Docker 이미지 빌드/푸시
# 5. (선택) dso_project manifest가 자동으로 업데이트되고, ArgoCD가 새 이미지로 배포
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

