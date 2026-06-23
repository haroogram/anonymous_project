# anonymous_project

Django 기반의 교육/튜토리얼 웹사이트입니다.  
현재 운영 경로는 **컨테이너 이미지 빌드 -> `dso_project`의 Kubernetes 매니페스트 업데이트 -> ArgoCD 동기화 배포**입니다.

## 현재 아키텍처(요약)

- 앱 프레임워크: Django 5.2 (`requirements.txt`)
- 애플리케이션 엔트리: `entrypoint.sh` -> `migrate` -> `load_initial_data` -> `collectstatic` -> gunicorn
- 환경 설정:
  - 로컬 기본: `anonymous_project.settings.development` (`manage.py` 기본값)
  - 컨테이너 기본: `anonymous_project.settings.production` (`Dockerfile` ENV)
- 인프라/배포 연계:
  - 현재 저장소: 앱 코드 + Docker 이미지
  - `dso_project`: Terraform + k8s manifests + ArgoCD

## 주요 기능

- 메인/소개/검색 페이지
- 카테고리-튜토리얼-상세 페이지
- 자유게시판(첨부/댓글/알림)
- 회원가입/로그인/이메일 인증/비밀번호 재설정
- 방문자 통계 API (`/api/visitors/stats/`, `/api/visitors/detail/`)
- 헬스 체크 엔드포인트 (`/healthz/`)

## 빠른 시작 (로컬 개발)

### 1) 자동 설정

```bash
# Linux/macOS
chmod +x setup.sh
./setup.sh

# Windows PowerShell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\setup.ps1
```

자동 설정 항목:
- 가상환경 생성
- 의존성 설치 (`pip install -r requirements.txt`)
- `.env` 생성 (`.env.example` 복사)
- DB 마이그레이션
- 초기 데이터 로드(스크립트에 따라)
- 정적 파일 수집

### 2) 개발 서버 실행

```bash
# Linux/macOS
source venv/bin/activate
python manage.py runserver

# Windows PowerShell
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

브라우저: `http://127.0.0.1:8000`

## 수동 설정

```bash
python -m venv venv
source venv/bin/activate   # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env       # Windows: copy .env.example .env
python manage.py migrate
python manage.py load_initial_data
python manage.py collectstatic --noinput --clear
python manage.py runserver
```

## 환경 변수 / 설정

### 기본 동작

- `manage.py` 기본 settings: `anonymous_project.settings.development`
- `Dockerfile` 기본 settings: `anonymous_project.settings.production`

### 로컬 개발(기본 SQLite)

`.env` 예시:

```env
SECRET_KEY=django-insecure-dev-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

MariaDB를 로컬에서 쓰려면:

```env
DB_ENGINE=mysql
DB_NAME=anonymous_db
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

### 컨테이너/운영

- `entrypoint.sh`는 `USE_SSM_ENV=true`일 때 SSM Parameter Store에서 `.env`를 생성합니다.
- 기본 SSM 경로: `SSM_BASE_PATH=/dso-project` (환경변수로 변경 가능)
- 필수 값(대표): `SECRET_KEY`, `ALLOWED_HOSTS`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`

## 배포 (현재 기준)

### 권장/현재 운영 경로

1. 현재 저장소에서 Docker 이미지 빌드/푸시  
2. CI가 `dso_project/k8s-manifests`의 이미지 태그 갱신  
3. ArgoCD가 변경을 감지해 클러스터에 반영

관련 워크플로우:
- `.github/workflows/docker-build-push.yml`
  - Docker Hub 푸시
  - `dso_project` 매니페스트 이미지 태그 자동 업데이트
- `.github/workflows/dependency-audit.yml`
  - 의존성 점검

## 레거시 경로 (현재 기본 운영 아님)

아래 항목은 저장소에 파일/워크플로우가 남아 있지만, 현재 주 배포 방식이 아닙니다.

- Packer AMI 빌드 관련 파일: `packer/`, `packer.pkr.hcl`
- CodeDeploy 관련 스크립트: `scripts/`, `.github/workflows/deploy.yml`
- AMI 빌드 워크플로우: `.github/workflows/build-ami.yml`

## 프로젝트 구조

```text
anonymous_project/
├── anonymous_project/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── celery.py
├── main/
│   ├── views.py
│   ├── models.py
│   ├── urls.py
│   ├── middleware.py
│   ├── tasks.py
│   └── management/
├── templates/
├── static/
├── Dockerfile
├── entrypoint.sh
├── setup.sh
├── setup.ps1
├── requirements.txt
└── manage.py
```

## 기술 스택

- Python 3.12
- Django 5.2
- MariaDB / SQLite
- Redis / Celery / django-celery-beat
- Gunicorn
- django-environ / python-dotenv
- django-storages / boto3

## 참고

- 헬스 체크 엔드포인트는 애플리케이션 기준 `/healthz/` 입니다.
- 운영 인프라(Terraform, k8s manifests)는 `dso_project` 저장소에서 관리합니다.
