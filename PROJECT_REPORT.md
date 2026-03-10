# Anonymous Project 프로젝트

## 1. 프로젝트 개요

### 1.1 프로젝트 소개
Anonymous Project는 anonymous 스타일의 프로그래밍 교육 사이트를 Django 프레임워크로 구현한 프로젝트입니다. 네트워크, Linux, Python, AWS 등 다양한 IT 주제에 대한 튜토리얼과 교육 자료를 제공하는 온라인 학습 플랫폼입니다.

### 1.2 프로젝트 목적
- 프로그래밍과 인프라를 쉽고 재미있게 배울 수 있는 온라인 학습 사이트 제공
- 카테고리별로 체계적으로 구성된 튜토리얼 콘텐츠 제공
- 사용자 친화적인 UI/UX를 통한 학습 경험 향상

### 1.3 주요 기능
- 🏠 **메인 페이지**: 카테고리별 튜토리얼 소개
- 📚 **튜토리얼 페이지**: 카테고리별 주제 목록 (Network, Linux, Python, AWS)
- 📖 **상세 페이지**: 각 주제의 상세 내용 표시
- 🔍 **검색 기능**: 제목과 내용에서 키워드 검색
- 📊 **접속자 통계**: 실시간 접속자 수 추적 및 통계 제공
- 🎨 **반응형 디자인**: 모바일 및 데스크톱 지원
- 🎯 **깔끔한 UI/UX**: anonymous 스타일의 현대적인 디자인

## 2. 기술 스택

### 2.1 Backend
- **Python 3.x**: 프로그래밍 언어
- **Django 6.0**: 웹 프레임워크
- **Gunicorn**: WSGI HTTP 서버 (프로덕션)
- **Celery**: 비동기 작업 처리
- **django-celery-beat**: 주기적 작업 스케줄링

### 2.2 Database
- **MariaDB**: 관계형 데이터베이스 (프로덕션)
- **SQLite**: 개발 환경용 데이터베이스
- **PyMySQL**: MariaDB/MySQL 연결 드라이버

### 2.3 Cache & Message Broker
- **Redis**: 캐싱 및 Celery 메시지 브로커
- **django-redis**: Django Redis 캐시 백엔드

### 2.4 Frontend
- **HTML5/CSS3**: 마크업 및 스타일링
- **JavaScript**: 클라이언트 측 동작

### 2.5 배포 및 인프라
- **AWS EC2**: 서버 인프라
- **AWS CodeDeploy**: 자동 배포
- **AWS S3**: 정적 파일 저장 (선택사항)
- **Nginx**: 리버스 프록시 및 웹 서버
- **Supervisor**: 프로세스 관리
- **Packer**: 커스텀 AMI 빌드

### 2.6 개발 도구
- **django-environ**: 환경 변수 관리
- **python-dotenv**: .env 파일 로딩
- **django-storages**: S3 스토리지 지원
- **boto3**: AWS SDK

## 3. 시스템 아키텍처

### 3.1 애플리케이션 구조
```
anonymous_project/
├── anonymous_project/      # 프로젝트 설정
│   ├── settings/           # 설정 파일 (환경별 분리)
│   │   ├── base.py        # 공통 설정
│   │   ├── development.py # 개발 환경
│   │   └── production.py  # 배포 환경
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── celery.py          # Celery 설정
├── main/                   # 메인 앱
│   ├── models.py          # 데이터 모델
│   ├── views.py           # 뷰 함수
│   ├── urls.py            # URL 라우팅
│   ├── tasks.py           # Celery 작업
│   ├── middleware.py      # 미들웨어
│   ├── utils.py           # 유틸리티 함수
│   └── management/        # 관리 명령어
├── templates/             # HTML 템플릿
├── static/                # 정적 파일
└── scripts/               # 배포 스크립트
```

### 3.2 데이터 모델

#### Category (카테고리)
- 네트워크, Linux, Python, AWS 등 대분류
- 순서(order) 필드를 통한 정렬 지원
- 슬러그(slug)를 통한 URL 생성

#### Topic (주제)
- 카테고리 하위의 세부 주제
- 제목, 내용, 순서 정보 포함
- 카테고리와 다대일 관계

#### VisitorStats (접속자 통계)
- 일별 접속자 수 통계
- 접속자 수 및 고유 접속자 수 추적
- Celery를 통한 Redis → MariaDB 동기화

### 3.3 데이터 흐름

#### 접속자 통계 처리 흐름
1. 사용자 접속 시 미들웨어에서 Redis 카운트 증가
2. 실시간 통계는 Redis에서 조회
3. Celery Beat 작업이 매일 자정에 전날 데이터를 MariaDB에 동기화
4. 과거 데이터는 MariaDB에서 조회

## 4. 주요 기능 상세

### 4.1 튜토리얼 시스템
- 카테고리별 주제 목록 제공
- 사이드바를 통한 네비게이션
- 주제별 상세 내용 표시
- 순서(order) 기반 정렬

### 4.2 검색 기능
- 제목과 내용에서 키워드 검색 (대소문자 구분 없음)
- 카테고리별로 그룹화된 검색 결과
- 검색 결과 개수 표시

### 4.3 접속자 통계
- 실시간 접속자 수 표시 (Redis 기반)
- 일별 접속자 통계 (Redis → MariaDB 동기화)
- 고유 접속자 수 추적 (IP 기반 중복 제거)
- 누적 접속자 수 계산

### 4.4 캐싱 전략
- 개발 환경: 캐싱 비활성화 (디버깅 편의성)
- 프로덕션 환경: 24시간 캐시 적용
- Redis를 통한 페이지 캐싱

## 5. 배포 아키텍처

### 5.1 배포 환경
- **Public Subnet**: 일반 EC2 배포
- **Private Subnet**: Packer AMI를 통한 배포 (권장)

### 5.2 CI/CD 파이프라인
1. **GitHub Actions**: 코드 빌드 및 S3 업로드
2. **AWS CodeDeploy**: EC2 인스턴스에 자동 배포
3. **배포 스크립트**:
   - `before_install.sh`: 환경 준비
   - `after_install.sh`: 의존성 설치 및 마이그레이션
   - `application_stop.sh`: 애플리케이션 중지
   - `application_start.sh`: 애플리케이션 시작
   - `validate_service.sh`: 헬스 체크

### 5.3 인프라 구성
- **Nginx**: 리버스 프록시 및 정적 파일 서빙
- **Gunicorn**: Django 애플리케이션 서버
- **Supervisor**: Gunicorn, Celery Worker, Celery Beat 프로세스 관리
- **MariaDB**: 데이터베이스 서버
- **Redis**: 캐시 및 메시지 브로커

### 5.4 Packer AMI 빌드
Private Subnet 배포를 위한 커스텀 AMI 생성:
- Python 3, pip, venv
- AWS CodeDeploy Agent
- Nginx
- MariaDB Client
- Supervisor
- 기본 시스템 유틸리티

## 6. 개발 환경 설정

### 6.1 빠른 시작
```bash
# 자동 설정 스크립트 실행
chmod +x setup.sh
./setup.sh
```

자동 설정이 수행하는 작업:
- 가상환경 생성 및 활성화
- 의존성 설치
- .env 파일 생성
- 데이터베이스 마이그레이션
- 정적 파일 수집

### 6.2 환경 변수 설정
- `DJANGO_SETTINGS_MODULE`: 환경별 설정 선택
- `SECRET_KEY`: Django 시크릿 키
- `DEBUG`: 디버그 모드
- `ALLOWED_HOSTS`: 허용된 호스트
- 데이터베이스 연결 정보
- Redis 연결 정보

### 6.3 데이터베이스 마이그레이션
```bash
python manage.py migrate
python manage.py load_initial_data  # 초기 데이터 로드
```

## 7. 보안 고려사항

### 7.1 프로덕션 환경 보안
- `DEBUG=False` 설정
- `SECRET_KEY` 환경 변수 관리
- HTTPS 강제 (SECURE_SSL_REDIRECT)
- 보안 쿠키 설정 (SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE)
- ALLOWED_HOSTS 설정

### 7.2 데이터베이스 보안
- 전용 데이터베이스 사용자 생성
- 최소 권한 원칙 적용
- 환경 변수를 통한 민감 정보 관리

## 8. 모니터링 및 유지보수

### 8.1 로깅
- 애플리케이션 로그: `/home/ubuntu/app/logs/`
- Gunicorn 로그
- Celery Worker 로그
- Celery Beat 로그

### 8.2 프로세스 관리
- Supervisor를 통한 프로세스 모니터링
- 자동 재시작 설정
- 헬스 체크 스크립트

### 8.3 정기 작업
- Celery Beat를 통한 일일 접속자 통계 동기화
- 로그 로테이션
- 데이터베이스 백업

## 9. 향후 개선 사항

### 9.1 기능 개선
- 사용자 인증 시스템 추가
- 댓글 및 피드백 기능
- 북마크 기능
- 학습 진행도 추적

### 9.2 성능 개선
- CDN을 통한 정적 파일 최적화
- 데이터베이스 쿼리 최적화
- 추가 캐싱 전략 적용

### 9.3 인프라 개선
- 로드 밸런서 도입
- 다중 가용 영역 배포
- 자동 스케일링 구성
- 모니터링 도구 통합 (CloudWatch, Sentry 등)

## 10. 참고 자료

### 10.1 프로젝트 문서
- `README.md`: 프로젝트 기본 문서
- `DEPLOYMENT.md`: 배포 가이드
- `CELERY_SETUP.md`: Celery 설정 가이드
- `CELERY_MONITORING.md`: Celery 모니터링 가이드
- `REDIS_SETUP.md`: Redis 설정 가이드
- `packer/README.md`: Packer AMI 빌드 가이드

### 10.2 주요 설정 파일
- `requirements.txt`: Python 패키지 의존성
- `appspec.yml`: CodeDeploy 배포 설정
- `packer.pkr.hcl`: Packer 빌드 설정
- `infrastructure.yaml`: 인프라 구성 (참고용)

---

**작성일**: 2026년 1월  
**프로젝트 버전**: Django 6.0  
**라이선스**: 학습 목적
