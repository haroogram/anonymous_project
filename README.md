# anonymous - Django 웹사이트

anonymous 스타일의 프로그래밍 교육 사이트를 Django 프레임워크로 구현한 프로젝트입니다.

## 기능

- 🏠 메인 페이지: 카테고리별 튜토리얼 소개
- 📚 튜토리얼 페이지: 카테고리별 주제 목록
- 📖 상세 페이지: 각 주제의 상세 내용
- 🎨 반응형 디자인: 모바일 및 데스크톱 지원
- 🎯 깔끔한 UI/UX: anonymous 스타일의 현대적인 디자인

## 설치 및 실행

### 빠른 시작 (자동 설정)

프로젝트를 클론한 후, 해당 디렉토리에서 다음 명령어 하나만 실행하면 환경 설정이 자동으로 완료됩니다:

```bash
# Linux/Mac
chmod +x setup.sh
./setup.sh

# Windows PowerShell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
.\setup.ps1
```

스크립트가 자동으로 다음 작업을 수행합니다:
- ✅ 가상환경 생성 및 활성화
- ✅ 의존성 설치 (pip install -r requirements.txt)
- ✅ .env 파일 생성 (.env.example 복사 또는 기본값 생성)
- ✅ 데이터베이스 마이그레이션 실행
- ✅ 정적 파일 수집

설정 완료 후 개발 서버 실행:

```bash
# Linux/Mac
source venv/bin/activate
python manage.py runserver

# Windows
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

---

### 수동 설정 (선택사항)

자동 설정 스크립트를 사용하지 않는 경우, 아래 단계를 수동으로 진행할 수 있습니다.

#### 1. 가상환경 활성화

```bash
# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

#### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

#### 3. 환경 변수 설정

```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일을 열어서 필요한 값 설정
# 개발 환경에서는 기본값으로도 동작합니다
```

#### 4. 데이터베이스 설정

#### 개발 환경

**옵션 1: SQLite 사용 (기본값)**
- 환경 변수 설정 없이 바로 사용 가능
- 별도 데이터베이스 서버 설치 불필요

**옵션 2: MariaDB 사용**
`.env` 파일에 다음을 추가:

```env
DB_ENGINE=mysql
DB_NAME=anonymous_db
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

MariaDB 설치 및 데이터베이스 생성:

```bash
# MariaDB 설치 (Ubuntu)
sudo apt update
sudo apt install mariadb-server

# MariaDB 접속
sudo mysql -u root -p

# 데이터베이스 생성
CREATE DATABASE anonymous_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 사용자 생성 및 권한 부여 (선택사항)
CREATE USER 'db_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON anonymous_db.* TO 'db_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 프로덕션 환경

`.env` 파일에 다음을 필수로 설정:

```env
DB_NAME=anonymous_db
DB_USER=db_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=3306
```

### 5. 데이터베이스 마이그레이션

```bash
python manage.py migrate
```

### 6. 개발 서버 실행

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
- MariaDB (데이터베이스)
- PyMySQL (MariaDB/MySQL 연결)
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

# 데이터베이스 설정 (선택사항)
# MariaDB 사용 시:
DB_ENGINE=mysql
DB_NAME=anonymous_db
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306

# SQLite 사용 시 (기본값):
# DB_ENGINE 설정하지 않으면 SQLite 사용
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

# 데이터베이스 설정 (필수)
DB_NAME=anonymous_db
DB_USER=db_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=3306
```

## AMI 빌드 (Packer)

**Private Subnet 배포 시 필수**: 인터넷 접근이 없는 Private Subnet에 배포하는 경우, Packer를 사용하여 필요한 소프트웨어가 미리 설치된 커스텀 AMI를 생성해야 합니다.

### Packer를 사용한 AMI 생성

1. **Packer 설치**: [Packer 공식 사이트](https://www.packer.io/downloads)에서 설치

2. **변수 설정 파일 생성**:
   ```bash
   cp packer/variables.pkr.hcl.example packer/variables.pkr.hcl
   # packer/variables.pkr.hcl 파일을 열어 실제 VPC, Subnet ID 등 입력
   ```

3. **AMI 빌드**:
   ```bash
   packer validate -var-file=packer/variables.pkr.hcl packer.pkr.hcl
   packer build -var-file=packer/variables.pkr.hcl packer.pkr.hcl
   ```

4. **빌드된 AMI 확인**: 출력된 AMI ID를 사용하여 EC2 인스턴스 생성

**상세 가이드**: `packer/README.md` 참조

### AMI에 포함된 소프트웨어

- ✅ Python 3, pip, venv
- ✅ AWS CodeDeploy Agent
- ✅ Nginx (웹 서버)
- ✅ MariaDB Client
- ✅ Supervisor (프로세스 관리)
- ✅ 기본 시스템 유틸리티

---

## 배포

### Private Subnet 배포 (권장)

1. **커스텀 AMI 사용**: 위 Packer 가이드에 따라 생성한 AMI 사용
2. **EC2 인스턴스 생성**: Private Subnet에 배치
3. **CodeDeploy Agent 시작**:
   ```bash
   sudo systemctl start codedeploy-agent
   sudo systemctl enable codedeploy-agent
   ```
4. **CodeDeploy 배포**: 아래 배포 절차 참조

### EC2 Ubuntu 서버에 배포 (Public Subnet)

일반적인 EC2 Ubuntu 서버에 배포 시:

1. MariaDB 설치 및 데이터베이스 생성:
   ```bash
   sudo apt update
   sudo apt install mariadb-server
   sudo mysql_secure_installation
   
   # 데이터베이스 생성
   sudo mysql -u root -p
   CREATE DATABASE anonymous_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'db_user'@'localhost' IDENTIFIED BY 'your_secure_password';
   GRANT ALL PRIVILEGES ON anonymous_db.* TO 'db_user'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;
   ```

2. `.env` 파일을 서버에 생성하고 프로덕션 값 설정 (데이터베이스 정보 포함)

3. `DJANGO_SETTINGS_MODULE` 환경 변수 설정:
   ```bash
   export DJANGO_SETTINGS_MODULE=anonymous_project.settings.production
   ```

4. 데이터베이스 마이그레이션:
   ```bash
   python manage.py migrate
   ```

5. 초기 데이터 로드 (카테고리 및 주제 데이터):
   ```bash
   python manage.py load_initial_data
   ```
   > **참고**: 개발 환경에서 이미 데이터를 입력했다면 이 단계는 생략할 수 있습니다. 하지만 프로덕션은 새로운 MariaDB이므로 초기 데이터를 로드해야 합니다.

6. `python manage.py collectstatic` 실행

7. Gunicorn으로 서버 실행:
   ```bash
   gunicorn anonymous_project.wsgi:application
   ```

8. Nginx를 리버스 프록시로 설정

> **중요 참고사항**: 
> - 프로덕션 환경에서는 `DJANGO_SETTINGS_MODULE=anonymous_project.settings.production`이 설정되면 자동으로 MariaDB를 사용합니다.
> - 코드(models.py, views.py 등)는 Django ORM을 사용하므로 SQLite든 MariaDB든 동일하게 동작합니다.
> - 개발 환경(SQLite)과 프로덕션 환경(MariaDB) 간 데이터베이스는 별개이므로, 프로덕션 배포 시 마이그레이션과 초기 데이터 로드를 다시 수행해야 합니다.

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
