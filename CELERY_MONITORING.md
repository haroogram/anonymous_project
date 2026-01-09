# Celery & Celery Beat 동작 확인 가이드

이 문서는 프로젝트에서 Celery Worker와 Celery Beat가 정상적으로 동작하고 있는지 확인하는 방법을 설명합니다.

## 1. 프로세스 상태 확인

### Supervisor를 통한 확인 (프로덕션 환경)

```bash
# Supervisor 상태 확인
sudo supervisorctl status

# Celery Worker 상태 확인
sudo supervisorctl status celery_worker

# Celery Beat 상태 확인
sudo supervisorctl status celery_beat

# 모든 프로세스 시작
sudo supervisorctl start celery_worker
sudo supervisorctl start celery_beat

# 모든 프로세스 재시작
sudo supervisorctl restart celery_worker
sudo supervisorctl restart celery_beat

# 실시간 로그 확인
sudo supervisorctl tail -f celery_worker
sudo supervisorctl tail -f celery_beat
```

### systemd를 통한 확인 (또는 직접 실행)

```bash
# systemd 서비스 상태 확인
sudo systemctl status celery-worker
sudo systemctl status celery-beat

# 또는 프로세스 직접 확인
ps aux | grep celery
```

## 2. Celery Worker 연결 및 상태 확인

**⚠️ 중요: 가상환경 사용 필요**

Celery 명령어는 가상환경에 설치되어 있습니다. 다음 중 하나의 방법을 사용하세요:

**방법 1: 가상환경 활성화 (권장)**
```bash
# 가상환경 활성화
source /home/ubuntu/venv/bin/activate  # 또는 source venv/bin/activate

# 이제 celery 명령어 사용 가능
celery -A anonymous_project inspect ping
```

**방법 2: 가상환경 경로 직접 사용**
```bash
# 프로젝트 디렉토리로 이동
cd /home/ubuntu/anonymous_project

# 환경 변수 설정 후 실행 (프로덕션 환경)
DJANGO_SETTINGS_MODULE=anonymous_project.settings.production /home/ubuntu/venv/bin/celery -A anonymous_project inspect ping

# 또는 개발 환경
DJANGO_SETTINGS_MODULE=anonymous_project.settings.development /home/ubuntu/venv/bin/celery -A anonymous_project inspect ping
```

**방법 3: Celery 앱을 명시적으로 지정**
```bash
# 프로젝트 디렉토리로 이동 필수
cd /home/ubuntu/anonymous_project

# Celery 앱을 명시적으로 지정
/home/ubuntu/venv/bin/celery -A anonymous_project.celery:app inspect ping
```

### 기본 연결 테스트

**⚠️ 중요: 프로젝트 디렉토리에서 실행해야 합니다!**

```bash
# 프로젝트 디렉토리로 이동 (필수!)
cd /home/ubuntu/anonymous_project

# 환경 변수 설정 후 실행
# 프로덕션 환경인 경우:
DJANGO_SETTINGS_MODULE=anonymous_project.settings.production /home/ubuntu/venv/bin/celery -A anonymous_project inspect ping

# 개발 환경인 경우:
DJANGO_SETTINGS_MODULE=anonymous_project.settings.development /home/ubuntu/venv/bin/celery -A anonymous_project inspect ping

# 또는 Celery 앱을 명시적으로 지정 (더 확실함):
/home/ubuntu/venv/bin/celery -A anonymous_project.celery:app inspect ping

# 모든 Worker 상태 확인
/home/ubuntu/venv/bin/celery -A anonymous_project.celery:app inspect active

# 등록된 작업 목록 확인
/home/ubuntu/venv/bin/celery -A anonymous_project.celery:app inspect registered

# Worker 통계 정보
/home/ubuntu/venv/bin/celery -A anonymous_project.celery:app inspect stats
```

**참고:** `-A anonymous_project` 대신 `-A anonymous_project.celery:app`을 사용하면 Django 설정 로드 문제를 피할 수 있습니다.

### 실시간 모니터링

```bash
# 프로젝트 디렉토리에서 실행
cd /home/ubuntu/anonymous_project

# 활성 작업 실시간 모니터링
/home/ubuntu/venv/bin/celery -A anonymous_project.celery:app events

# 특정 Worker의 작업 모니터링
/home/ubuntu/venv/bin/celery -A anonymous_project.celery:app inspect active_queues
```

## 3. Celery Beat 스케줄 확인

### 스케줄 정보 확인

```bash
# 프로젝트 디렉토리에서 실행
cd /home/ubuntu/anonymous_project

# Beat 스케줄 확인 (Dry-run 모드 - 실제 실행 없이 확인)
DJANGO_SETTINGS_MODULE=anonymous_project.settings.production /home/ubuntu/venv/bin/celery -A anonymous_project.celery:app beat --loglevel=info --dry-run

# Beat 스케줄 확인 (일반 실행 모드)
DJANGO_SETTINGS_MODULE=anonymous_project.settings.production /home/ubuntu/venv/bin/celery -A anonymous_project.celery:app beat --loglevel=debug
```

### Django Admin에서 스케줄 확인

1. Django Admin 페이지 접속: `/admin/`
2. "PERIODIC TASKS" 섹션으로 이동
3. `Periodic Tasks`와 `Crontabs` 또는 `Intervals` 확인
4. 등록된 작업이 올바르게 설정되어 있는지 확인

### 데이터베이스에서 직접 확인

```bash
# Django shell에서
python manage.py shell

>>> from django_celery_beat.models import PeriodicTask
>>> tasks = PeriodicTask.objects.all()
>>> for task in tasks:
...     print(f"Task: {task.name}, Enabled: {task.enabled}, Schedule: {task.schedule}")
```

## 4. 작업 수동 실행 테스트

### Django Shell에서 테스트

```bash
python manage.py shell
```

```python
# 작업 수동 실행
from main.tasks import sync_visitor_stats_task

# 비동기 실행 (Worker가 처리)
result = sync_visitor_stats_task.delay()
print(f"Task ID: {result.id}")

# 결과 확인 (동기 대기)
result.get(timeout=60)  # 60초 타임아웃

# 또는 결과만 확인
print(result.get())
```

### Celery 명령줄에서 직접 실행

```bash
# 프로젝트 디렉토리에서 실행
cd /home/ubuntu/anonymous_project

# 작업 즉시 실행 (Worker를 통해)
DJANGO_SETTINGS_MODULE=anonymous_project.settings.production /home/ubuntu/venv/bin/celery -A anonymous_project.celery:app call main.tasks.sync_visitor_stats_task
```

## 5. Redis 연결 확인

### Redis 연결 테스트

```bash
# Redis 서버 연결 확인
redis-cli ping
# 응답: PONG

# 또는 Python으로 테스트
python manage.py shell
```

```python
from django.core.cache import cache
cache.set('test_key', 'test_value', 30)
value = cache.get('test_key')
print(value)  # 'test_value' 출력되어야 함
```

### Redis에서 Celery 큐 확인

```bash
# Redis CLI 접속
redis-cli

# Celery 관련 키 확인
KEYS celery*

# 작업 큐 확인
KEYS celery-task-meta-*

# 특정 작업 결과 확인 (task_id 필요)
GET celery-task-meta-<task_id>
```

## 6. 로그 파일 확인

### 로그 파일 위치

- Celery Worker 로그: `/home/ubuntu/anonymous_project/logs/celery_worker.log`
- Celery Beat 로그: `/home/ubuntu/anonymous_project/logs/celery_beat.log`

### 로그 확인 명령어

```bash
# 실시간 로그 확인
tail -f /home/ubuntu/anonymous_project/logs/celery_worker.log
tail -f /home/ubuntu/anonymous_project/logs/celery_beat.log

# 최근 로그 확인 (마지막 100줄)
tail -n 100 /home/ubuntu/anonymous_project/logs/celery_worker.log

# 에러 로그만 확인
grep -i error /home/ubuntu/anonymous_project/logs/celery_worker.log

# 특정 작업 실행 로그 확인
grep "sync_visitor_stats_task" /home/ubuntu/anonymous_project/logs/celery_worker.log
```

## 7. Flower를 사용한 웹 기반 모니터링 (선택사항)

### Flower 설치 및 실행

```bash
# 가상환경 활성화 후
source /home/ubuntu/venv/bin/activate
pip install flower

# 프로젝트 디렉토리에서 실행
cd /home/ubuntu/anonymous_project

# Flower 실행
DJANGO_SETTINGS_MODULE=anonymous_project.settings.production /home/ubuntu/venv/bin/celery -A anonymous_project.celery:app flower --port=5555
```

### Flower 접속

웹 브라우저에서 `http://localhost:5555` (또는 서버 IP:5555) 접속

Flower에서 확인 가능한 정보:
- 활성 작업 (Active Tasks)
- 예약된 작업 (Scheduled Tasks)
- Worker 상태 및 통계
- 작업 실행 이력
- 작업 결과

## 8. 정상 동작 확인 체크리스트

- [ ] Redis 서버가 실행 중이고 연결 가능한가? (`redis-cli ping` → `PONG`)
- [ ] Celery Worker 프로세스가 실행 중인가? (`supervisorctl status celery_worker` → `RUNNING`)
- [ ] Celery Beat 프로세스가 실행 중인가? (`supervisorctl status celery_beat` → `RUNNING`)
- [ ] Worker가 작업을 등록했는가? (`/home/ubuntu/venv/bin/celery -A anonymous_project inspect registered`)
- [ ] Beat 스케줄이 올바르게 설정되어 있는가? (Django Admin 확인)
- [ ] 수동 작업 실행이 성공하는가? (Django shell에서 테스트)
- [ ] 로그에 에러가 없는가? (로그 파일 확인)
- [ ] 스케줄된 작업이 정시에 실행되는가? (로그 모니터링)

## 9. 문제 해결

### Worker가 작업을 처리하지 않음

```bash
# 1. Worker 재시작
sudo supervisorctl restart celery_worker

# 2. Worker 상태 확인 (프로젝트 디렉토리에서 실행)
cd /home/ubuntu/anonymous_project
DJANGO_SETTINGS_MODULE=anonymous_project.settings.production /home/ubuntu/venv/bin/celery -A anonymous_project.celery:app inspect active

# 3. 로그 확인
tail -f /home/ubuntu/anonymous_project/logs/celery_worker.log
```

### Beat가 작업을 스케줄하지 않음

```bash
# 1. Beat 재시작
sudo supervisorctl restart celery_beat

# 2. 스케줄 확인 (프로젝트 디렉토리에서 실행)
cd /home/ubuntu/anonymous_project
DJANGO_SETTINGS_MODULE=anonymous_project.settings.production /home/ubuntu/venv/bin/celery -A anonymous_project.celery:app beat --dry-run

# 3. 로그 확인
tail -f /home/ubuntu/anonymous_project/logs/celery_beat.log

# 4. Django Admin에서 Periodic Task가 활성화되어 있는지 확인
```

### Redis 연결 실패

```bash
# 1. Redis 서버 상태 확인
sudo systemctl status redis  # 또는 redis-server

# 2. Redis 연결 테스트
redis-cli ping

# 3. 환경 변수 확인
echo $REDIS_HOST
echo $REDIS_PORT

# 4. Django 설정 확인
python manage.py shell
>>> from django.conf import settings
>>> print(settings.CELERY_BROKER_URL)
```

### 작업이 실행되었지만 실패함

```bash
# 1. 로그에서 에러 확인
grep -i error /home/ubuntu/anonymous_project/logs/celery_worker.log

# 2. Django shell에서 직접 실행하여 에러 확인
python manage.py shell
>>> from main.tasks import sync_visitor_stats_task
>>> result = sync_visitor_stats_task()  # 동기 실행 (에러 추적 용이)
>>> print(result)
```

### "Module 'anonymous_project' has no attribute 'celery'" 에러

이 에러는 Celery가 Django 설정을 로드하지 못하거나 프로젝트 디렉토리에서 실행하지 않아서 발생합니다.

**해결 방법:**

1. **프로젝트 디렉토리에서 실행 (필수!)**
```bash
cd /home/ubuntu/anonymous_project
```

2. **Celery 앱을 명시적으로 지정**
```bash
# -A anonymous_project 대신 -A anonymous_project.celery:app 사용
/home/ubuntu/venv/bin/celery -A anonymous_project.celery:app inspect ping
```

3. **DJANGO_SETTINGS_MODULE 환경 변수 설정**
```bash
DJANGO_SETTINGS_MODULE=anonymous_project.settings.production /home/ubuntu/venv/bin/celery -A anonymous_project.celery:app inspect ping
```

4. **가상환경 활성화 후 프로젝트 디렉토리에서 실행**
```bash
source /home/ubuntu/venv/bin/activate
cd /home/ubuntu/anonymous_project
DJANGO_SETTINGS_MODULE=anonymous_project.settings.production celery -A anonymous_project.celery:app inspect ping
```

**참고:** `celery.py` 파일이 `anonymous_project/celery.py`에 있는지 확인하세요.

## 10. 자동화된 헬스체크 스크립트

다음 스크립트를 사용하여 한 번에 모든 상태를 확인할 수 있습니다:

```bash
#!/bin/bash
# celery-health-check.sh

echo "=== Celery Health Check ==="
echo ""

echo "1. Redis 연결 확인:"
redis-cli ping || echo "❌ Redis 연결 실패"
echo ""

echo "2. Celery Worker 상태:"
cd ${PROJECT_DIR} && DJANGO_SETTINGS_MODULE=anonymous_project.settings.production ${VENV_DIR}/bin/celery -A anonymous_project.celery:app inspect ping || echo "❌ Worker 연결 실패"
echo ""

echo "3. Supervisor 프로세스 상태:"
sudo supervisorctl status celery_worker celery_beat
echo ""

echo "4. 등록된 작업 목록:"
cd ${PROJECT_DIR} && DJANGO_SETTINGS_MODULE=anonymous_project.settings.production ${VENV_DIR}/bin/celery -A anonymous_project.celery:app inspect registered | head -20
echo ""

echo "5. 활성 작업:"
cd ${PROJECT_DIR} && DJANGO_SETTINGS_MODULE=anonymous_project.settings.production ${VENV_DIR}/bin/celery -A anonymous_project.celery:app inspect active
echo ""

echo "6. 최근 로그 (마지막 10줄):"
tail -n 10 /home/ubuntu/anonymous_project/logs/celery_worker.log 2>/dev/null || echo "로그 파일을 찾을 수 없습니다"
```

이 스크립트를 실행 가능하게 만든 후 실행:

```bash
chmod +x celery-health-check.sh
./celery-health-check.sh
```

## 11. 빠른 참조 - 즉시 사용 가능한 명령어

### 가상환경 활성화 없이 바로 사용

```bash
# 프로젝트 디렉토리로 이동 (필수!)
cd /home/ubuntu/anonymous_project

# Worker 연결 확인
DJANGO_SETTINGS_MODULE=anonymous_project.settings.production /home/ubuntu/venv/bin/celery -A anonymous_project.celery:app inspect ping

# 등록된 작업 확인
DJANGO_SETTINGS_MODULE=anonymous_project.settings.production /home/ubuntu/venv/bin/celery -A anonymous_project.celery:app inspect registered

# 활성 작업 확인
DJANGO_SETTINGS_MODULE=anonymous_project.settings.production /home/ubuntu/venv/bin/celery -A anonymous_project.celery:app inspect active

# Worker 통계 확인
DJANGO_SETTINGS_MODULE=anonymous_project.settings.production /home/ubuntu/venv/bin/celery -A anonymous_project.celery:app inspect stats
```

### 가상환경 활성화 후 사용 (더 편리함)

```bash
# 가상환경 활성화
source /home/ubuntu/venv/bin/activate

# 프로젝트 디렉토리로 이동 (필수!)
cd /home/ubuntu/anonymous_project

# 환경 변수 설정 후 celery 명령어 사용
DJANGO_SETTINGS_MODULE=anonymous_project.settings.production celery -A anonymous_project.celery:app inspect ping
DJANGO_SETTINGS_MODULE=anonymous_project.settings.production celery -A anonymous_project.celery:app inspect registered
DJANGO_SETTINGS_MODULE=anonymous_project.settings.production celery -A anonymous_project.celery:app inspect active
```

### Supervisor로 프로세스 관리

```bash
# 상태 확인
sudo supervisorctl status celery_worker celery_beat

# 시작
sudo supervisorctl start celery_worker celery_beat

# 재시작
sudo supervisorctl restart celery_worker celery_beat

# 로그 확인
sudo supervisorctl tail -f celery_worker
sudo supervisorctl tail -f celery_beat
```

### 작업 수동 테스트

```bash
# Django shell 실행
python manage.py shell

# 작업 실행
>>> from main.tasks import sync_visitor_stats_task
>>> result = sync_visitor_stats_task.delay()
>>> result.get()  # 결과 확인
```

### 로그 확인

```bash
# 실시간 로그 확인
tail -f /home/ubuntu/anonymous_project/logs/celery_worker.log
tail -f /home/ubuntu/anonymous_project/logs/celery_beat.log

# 에러 확인
grep -i error /home/ubuntu/anonymous_project/logs/celery_worker.log
```

