# 빠른 배포 시작 가이드

## 1. GitHub Secrets 설정 (필수)

GitHub 저장소의 **Settings > Secrets and variables > Actions**에서 다음 Secrets를 추가하세요:

```
AWS_ACCESS_KEY_ID: AWS 액세스 키 ID
AWS_SECRET_ACCESS_KEY: AWS 시크릿 액세스 키
S3_BUCKET: S3 버킷 이름 (예: my-deployment-bucket)
CODE_DEPLOY_APPLICATION: CodeDeploy 애플리케이션 이름 (예: anonymous-project)
CODE_DEPLOY_DEPLOYMENT_GROUP: 배포 그룹 이름 (예: production)
```

## 2. appspec.yml 확인

`appspec.yml` 파일의 경로와 사용자 이름이 EC2 인스턴스 설정과 일치하는지 확인하세요:

```yaml
destination: /home/ubuntu/app  # EC2 인스턴스의 앱 디렉토리
owner: ubuntu
group: ubuntu
```

## 3. 배포 스크립트 실행 권한

EC2 인스턴스에서 처음 배포하기 전에 스크립트에 실행 권한이 있는지 확인하세요:

```bash
chmod +x /home/ubuntu/app/scripts/*.sh
```

## 4. 첫 배포 전 EC2 설정

EC2 인스턴스에서 다음 명령어를 실행하세요:

```bash
# CodeDeploy Agent 설치 (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y ruby wget
cd /home/ubuntu
wget https://aws-codedeploy-ap-northeast-2.s3.ap-northeast-2.amazonaws.com/latest/install
chmod +x ./install
sudo ./install auto

# Python 및 필요한 패키지
sudo apt-get install -y python3.12 python3.12-venv python3-pip

# 프로젝트 디렉토리 생성
sudo mkdir -p /home/ubuntu/app
sudo chown -R ubuntu:ubuntu /home/ubuntu/app

# 환경 변수 파일 생성
sudo touch /home/ubuntu/app/.env
sudo chown ubuntu:ubuntu /home/ubuntu/app/.env
# .env 파일에 필요한 환경 변수 추가 (DEPLOYMENT.md 참고)
```

## 5. 배포 실행

1. `main` 브랜치에 코드를 푸시하면 자동 배포가 시작됩니다
2. 또는 GitHub Actions 페이지에서 "Run workflow" 버튼으로 수동 실행 가능

## 문제 발생 시

자세한 배포 가이드는 [DEPLOYMENT.md](./DEPLOYMENT.md)를 참고하세요.

