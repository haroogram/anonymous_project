# Celery Beat 설정 및 실행 가이드

이 프로젝트는 Celery Beat를 사용하여 매일 자정에 접속자 수 통계를 MariaDB에 동기화합니다.

## 설치

```bash
pip install -r requirements.txt
```

## 마이그레이션

django-celery-beat가 사용하는 테이블을 생성하기 위해 마이그레이션을 실행합니다:

```bash
python manage.py migrate
```

## 실행 방법

### 개발 환경 (로컬)

#### 1. Redis 실행 (별도 터미널)
```bash
# Docker 사용
docker run -d -p 6379:6379 --name redis redis:latest

# 또는 로컬 Redis 서버 실행
redis-server
```

#### 2. Celery Worker 실행 (별도 터미널)
```bash
celery -A anonymous_project worker --loglevel=info
```

#### 3. Celery Beat 실행 (별도 터미널)
```bash
celery -A anonymous_project beat --loglevel=info
```

#### 4. Django 개발 서버 실행 (별도 터미널)
```bash
python manage.py runserver
```

### 프로덕션 환경 (AWS EC2 + ASG)

각 EC2 인스턴스에서 systemd를 사용하여 서비스로 실행하는 것을 권장합니다.

#### 1. Celery Worker 서비스 파일 생성

`/etc/systemd/system/celery-worker.service`:

```ini
[Unit]
Description=Celery Worker Service
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/anonymous_project
Environment="DJANGO_SETTINGS_MODULE=anonymous_project.settings.production"
EnvironmentFile=/path/to/anonymous_project/.env
ExecStart=/path/to/venv/bin/celery -A anonymous_project worker --loglevel=info --logfile=/var/log/celery/worker.log
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 2. Celery Beat 서비스 파일 생성

`/etc/systemd/system/celery-beat.service`:

```ini
[Unit]
Description=Celery Beat Service
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/anonymous_project
Environment="DJANGO_SETTINGS_MODULE=anonymous_project.settings.production"
EnvironmentFile=/path/to/anonymous_project/.env
ExecStart=/path/to/venv/bin/celery -A anonymous_project beat --loglevel=info --logfile=/var/log/celery/beat.log
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 3. 로그 디렉토리 생성

```bash
sudo mkdir -p /var/log/celery
sudo chown www-data:www-data /var/log/celery
```

#### 4. 서비스 시작 및 활성화

```bash
# Celery Worker
sudo systemctl daemon-reload
sudo systemctl enable celery-worker
sudo systemctl start celery-worker
sudo systemctl status celery-worker

# Celery Beat (한 인스턴스에서만 실행되어야 함 - Redis 락으로 보장됨)
sudo systemctl enable celery-beat
sudo systemctl start celery-beat
sudo systemctl status celery-beat
```

## ASG 환경에서의 주의사항

### Celery Beat는 단일 인스턴스에서만 실행

Celery Beat는 Redis 기반 분산 락을 사용하여 여러 인스턴스가 있어도 **단 하나의 Beat 프로세스만 실행**됩니다.

- 각 인스턴스에서 Beat 서비스를 시작해도 됩니다
- Redis 락 덕분에 실제로는 하나만 실행됩니다
- Beat가 실행 중인 인스턴스가 종료되면 다른 인스턴스의 Beat가 자동으로 실행됩니다

### Celery Worker는 모든 인스턴스에서 실행

- 모든 EC2 인스턴스에서 Worker를 실행하는 것을 권장합니다
- 작업이 여러 Worker에 분산되어 처리됩니다
- 인스턴스가 종료되어도 다른 Worker가 작업을 처리합니다

## 스케줄 관리

### Django Admin에서 스케줄 관리

django-celery-beat를 사용하면 Django Admin에서 스케줄을 관리할 수 있습니다:

1. Admin 페이지 접속: `/admin/`
2. "PERIODIC TASKS" 섹션에서 스케줄 확인 및 수정

### 코드에서 스케줄 정의

`anonymous_project/settings/base.py`의 `CELERY_BEAT_SCHEDULE`에서 스케줄을 정의합니다:

```python
CELERY_BEAT_SCHEDULE = {
    'sync-visitor-stats-daily': {
        'task': 'main.tasks.sync_visitor_stats_task',
        'schedule': crontab(hour=0, minute=1),  # 매일 자정 1분
        'options': {'expires': 60 * 60},  # 작업 만료 시간 (1시간)
    },
}
```

## 테스트

### 1. 작업 수동 실행 테스트

```bash
# Django shell에서
python manage.py shell

>>> from main.tasks import sync_visitor_stats_task
>>> result = sync_visitor_stats_task.delay()
>>> result.get()  # 결과 확인
```

### 2. Celery Worker 연결 테스트

```bash
# 별도 터미널에서
celery -A anonymous_project inspect active
celery -A anonymous_project inspect registered
```

### 3. Celery Beat 스케줄 확인

```bash
celery -A anonymous_project beat --loglevel=info --dry-run
```

## 모니터링 (선택사항)

### Flower 사용 (웹 기반 모니터링 도구)

```bash
pip install flower

# Flower 실행
celery -A anonymous_project flower
```

웹 브라우저에서 `http://localhost:5555` 접속하여 작업 상태를 모니터링할 수 있습니다.

## 문제 해결

### Redis 연결 실패

```bash
# Redis 연결 테스트
redis-cli ping
# 응답: PONG

# 또는
celery -A anonymous_project inspect ping
```

### 작업이 실행되지 않음

1. Celery Worker가 실행 중인지 확인
2. Celery Beat가 실행 중인지 확인
3. Redis 연결 상태 확인
4. 로그 확인: `/var/log/celery/worker.log`, `/var/log/celery/beat.log`

### Beat가 여러 개 실행됨

정상입니다. Redis 락 때문에 실제로는 하나만 실행됩니다. 로그에서 "beat: Starting..."과 "beat: Acquired lock" 메시지를 확인하세요.

### 마이그레이션 오류

```bash
python manage.py migrate django_celery_beat
```

## 환경 변수

프로덕션 환경의 `.env` 파일에 다음이 설정되어 있어야 합니다:

```env
DJANGO_SETTINGS_MODULE=anonymous_project.settings.production
REDIS_HOST=your-elasticache-endpoint.cache.amazonaws.com
REDIS_PORT=6379
REDIS_PASSWORD=your-auth-token  # AUTH 토큰이 설정된 경우
```

## 참고 자료

- [Celery 공식 문서](https://docs.celeryproject.org/)
- [django-celery-beat 문서](https://django-celery-beat.readthedocs.io/)

