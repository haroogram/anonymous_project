# anonymous_project

Django 기반의 교육/튜토리얼 웹 서비스입니다.  
단순 CRUD 앱이 아니라, 실서비스 운영 관점(배포 자동화/환경 분리/시크릿 관리/비동기 처리)까지 고려해 구성했습니다.

---

## 프로젝트 한눈에 보기

### 프로젝트 목적
- 학습 콘텐츠(카테고리/주제) 제공
- 사용자 인증 기반 게시판(첨부/댓글/알림) 제공
- 운영 환경에서 안정적으로 배포/확장 가능한 구조 구축

### 핵심 가치
- **개발/운영 분리**: `development` vs `production` 설정 분리
- **운영 자동화**: Docker 이미지 -> GitOps(ArgoCD) 배포
- **보안/환경 변수 관리**: SSM Parameter Store 기반 런타임 주입
- **성능/운영성 확보**: Redis 캐시, Celery 비동기 작업, health check

---

## 아키텍처 개요

### 실행/배포 흐름
1. `anonymous_project`에서 Docker 이미지 빌드/푸시
2. CI가 `dso_project/k8s-manifests`의 이미지 태그 갱신
3. ArgoCD가 변경 감지 후 K8s에 자동 반영
4. 컨테이너 `entrypoint.sh`가 SSM에서 환경변수 로드 후 앱 기동

### 런타임 초기화 순서
- `entrypoint.sh`
  - SSM -> `.env` 생성(`USE_SSM_ENV=true`일 때)
  - `migrate`
  - `load_initial_data`
  - `collectstatic`
  - gunicorn 실행

### 환경 설정
- 로컬 기본: `anonymous_project.settings.development` (`manage.py`)
- 컨테이너 기본: `anonymous_project.settings.production` (`Dockerfile`)
- 헬스 체크 엔드포인트: `/healthz/`

---

## 기능 요약

- 콘텐츠: 카테고리/튜토리얼/상세 페이지
- 커뮤니티: 게시판, 첨부파일, 댓글, 알림
- 인증: 회원가입, 로그인/로그아웃, 이메일 인증, 비밀번호 재설정
- 운영 API: 방문자 통계 API (`/api/visitors/stats/`, `/api/visitors/detail/`)

---

## 기술 스택과 선택 이유

- **Django 5.2**: 빠른 백엔드 생산성과 안정적인 ORM/인증 생태계
- **MariaDB / SQLite**: 운영/개발 DB 분리로 개발 편의 + 운영 안정성
- **Redis**: 캐시/카운팅/비동기 브로커로 응답성 및 확장성 개선
- **Celery + django-celery-beat**: 배치/주기 작업 분리로 웹 요청 처리 경량화
- **Gunicorn**: 운영 환경의 표준 WSGI 런타임
- **Docker + GitHub Actions + ArgoCD**: 빌드/배포 자동화 및 GitOps 운영
- **SSM Parameter Store**: 민감정보 중앙 관리 및 런타임 주입

---

## 코드/디렉터리 구조 (핵심만)

```text
anonymous_project/
├── anonymous_project/
│   ├── settings/              # base/development/production 분리
│   ├── urls.py
│   ├── wsgi.py
│   └── celery.py
├── main/                      # 핵심 도메인 앱
│   ├── views.py
│   ├── models.py
│   ├── middleware.py
│   ├── tasks.py
│   └── management/
├── templates/                 # 템플릿
├── static/                    # 정적 리소스
├── Dockerfile                 # 컨테이너 빌드
├── entrypoint.sh              # 런타임 초기화 + 기동
├── setup.sh / setup.ps1       # 로컬 개발 부트스트랩
└── .github/workflows/         # CI/CD 워크플로우
```

---

## 로컬 실행 방법 (개발자용)

### 자동 설정

```bash
# Linux/macOS
chmod +x setup.sh
./setup.sh

# Windows PowerShell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\setup.ps1
```

### 수동 설정

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

브라우저: `http://127.0.0.1:8000`

---

## 환경 변수 가이드

### 로컬(기본 SQLite)

```env
SECRET_KEY=django-insecure-dev-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 로컬 MariaDB 사용 시

```env
DB_ENGINE=mysql
DB_NAME=anonymous_db
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

### 운영(컨테이너)
- `USE_SSM_ENV=true` 설정 시 SSM에서 `.env` 자동 생성
- 기본 경로: `SSM_BASE_PATH=/dso-project`
- 필수 값(대표): `SECRET_KEY`, `ALLOWED_HOSTS`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`

---

## 배포 및 CI

- `.github/workflows/docker-build-push.yml`
  - Docker Hub 이미지 푸시
  - `dso_project` 매니페스트 이미지 태그 자동 업데이트
- `.github/workflows/dependency-audit.yml`
  - 의존성 보안 점검

---

## 레거시 경로 안내 (현재 기본 운영 아님)

현재 기본 운영은 Docker/K8s/GitOps입니다. 아래는 레거시 또는 참고용 자산입니다.

- Packer AMI 관련: `packer/`, `packer.pkr.hcl`
- CodeDeploy 관련: `scripts/`, `.github/workflows/deploy.yml`
- AMI 빌드 워크플로우: `.github/workflows/build-ami.yml`

