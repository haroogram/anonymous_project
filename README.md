# anonymous - Django 웹사이트

anonymous 스타일의 프로그래밍 교육 사이트를 Django 프레임워크로 구현한 프로젝트입니다.

## 기능

- 🏠 메인 페이지: 카테고리별 튜토리얼 소개
- 📚 튜토리얼 페이지: 카테고리별 주제 목록
- 📖 상세 페이지: 각 주제의 상세 내용
- 🎨 반응형 디자인: 모바일 및 데스크톱 지원
- 🎯 깔끔한 UI/UX: anonymous 스타일의 현대적인 디자인

## 설치 및 실행

### 1. 가상환경 활성화

```bash
# Windows
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일을 열어서 필요한 값 설정
# 개발 환경에서는 기본값으로도 동작합니다
```

### 4. 데이터베이스 마이그레이션

```bash
python manage.py migrate
```

### 5. 개발 서버 실행

```bash
python manage.py runserver
```

브라우저에서 `http://127.0.0.1:8000` 접속

## 프로젝트 구조

```
anonymous_project/
├── anonymous_project/      # 프로젝트 설정
│   ├── settings/           # 설정 파일 (환경별 분리)
│   │   ├── __init__.py
│   │   ├── base.py        # 공통 설정
│   │   ├── development.py # 개발 환경
│   │   └── production.py  # 배포 환경
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── main/                   # 메인 앱
│   ├── views.py
│   ├── urls.py
│   └── ...
├── templates/              # HTML 템플릿
│   └── main/
│       ├── base.html
│       ├── index.html
│       ├── tutorial.html
│       └── topic_detail.html
├── static/                 # 정적 파일
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── .env.example           # 환경 변수 예시
├── requirements.txt        # 의존성
└── manage.py
```

## 기술 스택

- Python 3.x
- Django 6.0
- python-dotenv (환경 변수 관리)
- HTML5/CSS3
- JavaScript

## 카테고리

- Network
- Linux
- Python
- AWS

## 환경 변수 설정

프로젝트는 `DJANGO_SETTINGS_MODULE` 환경 변수를 통해 개발/배포 환경을 구분합니다.

### 개발 환경 (기본값)

기본적으로 개발 환경 설정이 사용됩니다. `.env` 파일에 다음을 설정:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 배포 환경 (EC2 Ubuntu)

서버에서 `DJANGO_SETTINGS_MODULE` 환경 변수를 설정하여 프로덕션 설정을 사용합니다:

```bash
# 환경 변수 설정
export DJANGO_SETTINGS_MODULE=anonymous_project.settings.production

# 또는 .env 파일에 설정
DJANGO_SETTINGS_MODULE=anonymous_project.settings.production
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

## 배포

EC2 Ubuntu 서버에 배포 시:

1. `.env` 파일을 서버에 생성하고 프로덕션 값 설정
2. `DJANGO_SETTINGS_MODULE` 환경 변수 설정:
   ```bash
   export DJANGO_SETTINGS_MODULE=anonymous_project.settings.production
   ```
3. `python manage.py collectstatic` 실행
4. Gunicorn으로 서버 실행:
   ```bash
   gunicorn anonymous_project.wsgi:application
   ```
5. Nginx를 리버스 프록시로 설정

### systemd 서비스 파일 예시

```ini
[Unit]
Description=Gunicorn daemon for anonymous_project
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/anonymous_project
Environment="DJANGO_SETTINGS_MODULE=anonymous_project.settings.production"
ExecStart=/path/to/venv/bin/gunicorn anonymous_project.wsgi:application

[Install]
WantedBy=multi-user.target
```

## 라이선스

이 프로젝트는 학습 목적으로 제작되었습니다.
