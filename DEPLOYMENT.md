# 배포 가이드

이 프로젝트는 GitHub Actions와 AWS CodeDeploy를 사용하여 자동 배포됩니다.

## 사전 준비 사항

### 1. AWS 리소스 설정

#### S3 버킷 생성
```bash
aws s3 mb s3://your-s3-bucket-name --region ap-northeast-2
```

#### CodeDeploy 애플리케이션 및 배포 그룹 생성
```bash
# 애플리케이션 생성
aws deploy create-application \
  --application-name your-code-deploy-app \
  --compute-platform Server

# 배포 그룹 생성 (EC2 인스턴스용)
aws deploy create-deployment-group \
  --application-name your-code-deploy-app \
  --deployment-group-name your-deployment-group \
  --service-role-arn arn:aws:iam::YOUR_ACCOUNT_ID:role/CodeDeployServiceRole \
  --ec2-tag-filters Key=Name,Value=your-ec2-instance,Type=KEY_AND_VALUE
```

### 2. GitHub Secrets 설정

GitHub 저장소의 Settings > Secrets and variables > Actions에서 다음 Secrets를 설정하세요:

- `AWS_ACCESS_KEY_ID`: AWS 액세스 키 ID
- `AWS_SECRET_ACCESS_KEY`: AWS 시크릿 액세스 키
- `S3_BUCKET`: S3 버킷 이름
- `CODE_DEPLOY_APPLICATION`: CodeDeploy 애플리케이션 이름
- `CODE_DEPLOY_DEPLOYMENT_GROUP`: CodeDeploy 배포 그룹 이름

### 3. EC2 인스턴스 설정

#### CodeDeploy Agent 설치
```bash
sudo yum update -y
sudo yum install ruby -y
sudo yum install wget -y

cd /home/ec2-user
wget https://aws-codedeploy-ap-northeast-2.s3.ap-northeast-2.amazonaws.com/latest/install
chmod +x ./install
sudo ./install auto

# CodeDeploy Agent 상태 확인
sudo service codedeploy-agent status
```

#### 필요한 소프트웨어 설치
```bash
# Python 3.12 및 pip 설치
sudo apt-get update
sudo apt-get install -y python3.12 python3.12-venv python3-pip

# Nginx 설치 (선택사항)
sudo apt-get install -y nginx

# Supervisor 설치 (프로세스 관리용, 권장)
sudo apt-get install -y supervisor
```

#### 프로젝트 디렉토리 생성
```bash
sudo mkdir -p /home/ubuntu/app
sudo mkdir -p /home/ubuntu/logs
sudo chown -R ubuntu:ubuntu /home/ubuntu/app
sudo chown -R ubuntu:ubuntu /home/ubuntu/logs
```

### 4. 환경 변수 설정

EC2 인스턴스의 `/home/ubuntu/app/.env` 파일에 다음 환경 변수를 설정하세요:

```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# 데이터베이스 설정
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DB_PORT=3306

# Redis 설정
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
REDIS_DB=0

# 기타 설정
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 5. Supervisor 설정 (선택사항)

`/etc/supervisor/conf.d/anonymous_project.conf` 파일 생성:

```ini
[program:anonymous_project]
command=/home/ubuntu/venv/bin/gunicorn anonymous_project.wsgi:application --bind 0.0.0.0:8000 --workers 3
directory=/home/ubuntu/app
user=ubuntu
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/ubuntu/app/logs/gunicorn.log

[program:celery_worker]
command=/home/ubuntu/venv/bin/celery -A anonymous_project worker --loglevel=info
directory=/home/ubuntu/app
user=ubuntu
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/ubuntu/app/logs/celery_worker.log

[program:celery_beat]
command=/home/ubuntu/venv/bin/celery -A anonymous_project beat --loglevel=info
directory=/home/ubuntu/app
user=ubuntu
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/ubuntu/app/logs/celery_beat.log
```

Supervisor 재시작:
```bash
sudo supervisorctl reread
sudo supervisorctl update
```

### 6. 워크플로우 파일 수정

`.github/workflows/deploy.yml` 파일에서 다음 값을 수정하세요:

```yaml
env:
  AWS_REGION: ap-northeast-2  # 사용할 AWS 리전
  S3_BUCKET: your-s3-bucket-name  # GitHub Secrets에서 가져올 수도 있음
  CODE_DEPLOY_APPLICATION: your-code-deploy-app
  CODE_DEPLOY_DEPLOYMENT_GROUP: your-deployment-group
```

## 배포 프로세스

### 자동 배포

1. `main` 브랜치에 코드를 푸시하면 자동으로 배포가 시작됩니다.
2. GitHub Actions가 코드를 빌드하고 S3에 업로드합니다.
3. CodeDeploy가 배포를 트리거합니다.
4. EC2 인스턴스에서 배포 스크립트가 실행됩니다.

### 수동 배포

GitHub Actions 페이지에서 "Run workflow" 버튼을 클릭하여 수동으로 배포를 트리거할 수 있습니다.

## 배포 스크립트 설명

### before_install.sh
- 로그 디렉토리 생성
- 이전 배포 디렉토리 백업

### after_install.sh
- Python 가상환경 생성/활성화
- requirements.txt 설치
- Django static files 수집
- 데이터베이스 migrations 실행

### application_stop.sh
- 실행 중인 애플리케이션 중지 (Gunicorn, Supervisor, systemd 지원)

### application_start.sh
- 애플리케이션 시작 (Gunicorn, Supervisor, systemd 지원)
- Celery Worker 및 Beat 시작

### validate_service.sh
- 애플리케이션이 정상적으로 실행 중인지 확인
- Health check 수행

## 문제 해결

### CodeDeploy Agent 문제
```bash
# Agent 재시작
sudo service codedeploy-agent restart

# 로그 확인
sudo tail -f /var/log/aws/codedeploy-agent/codedeploy-agent.log
```

### 배포 실패 시
1. CodeDeploy 콘솔에서 배포 로그 확인
2. EC2 인스턴스의 `/opt/codedeploy-agent/deployment-root` 디렉토리 확인
3. 애플리케이션 로그 확인: `/home/ubuntu/app/logs/`

### 권한 문제
```bash
sudo chown -R ubuntu:ubuntu /home/ubuntu/app
chmod +x /home/ubuntu/app/scripts/*.sh
```

## 참고 사항

- 첫 배포 전에는 EC2 인스턴스에 필요한 소프트웨어가 설치되어 있어야 합니다.
- 환경 변수는 EC2 인스턴스에 직접 설정해야 합니다 (보안상 GitHub Secrets에 저장하지 않음).
- 데이터베이스 마이그레이션은 자동으로 실행되지만, 첫 배포 시에는 수동으로 초기 데이터를 로드해야 할 수 있습니다.

