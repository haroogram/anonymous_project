# Redis 접속자 수 추적 설정 가이드

이 프로젝트는 Redis를 사용하여 일별 및 누적 접속자 수를 추적합니다.

## 기능

- 📊 **일별 접속자 수**: 오늘 날짜의 접속자 수 추적
- 📈 **누적 접속자 수**: 전체 누적 접속자 수 추적
- 🎯 **고유 접속자 수**: IP 기반 중복 제거를 통한 고유 접속자 수
- 📅 **과거 날짜 조회**: 특정 날짜의 접속자 수 조회 가능

## 로컬 개발 환경 설정 (Redis 로컬 설치)

### 1. Redis 설치

**Windows:**
```powershell
# Chocolatey 사용
choco install redis-64

# 또는 WSL2 사용
wsl
sudo apt update
sudo apt install redis-server
```

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install redis-server

# Mac (Homebrew)
brew install redis
```

### 2. Redis 실행

```bash
# Linux/Mac
redis-server

# Windows
redis-server
```

### 3. 환경 변수 설정

`.env` 파일에 Redis 설정 추가 (선택사항, 기본값 사용 가능):

```env
# 로컬 Redis (기본값)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
# REDIS_PASSWORD=  # 로컬에서는 보통 비밀번호 없음
```

## AWS ElastiCache for Redis 설정

### 1. ElastiCache 클러스터 생성

1. AWS 콘솔에서 ElastiCache 서비스로 이동
2. "Redis 클러스터 생성" 클릭
3. 설정 구성:
   - **클러스터 모드**: 비활성화 (단일 노드 또는 복제 그룹)
   - **엔진 버전**: Redis 6.x 이상 권장
   - **노드 타입**: 사용량에 맞게 선택 (예: `cache.t3.micro` - 프리 티어)
   - **서브넷 그룹**: VPC 및 서브넷 설정
   - **보안 그룹**: EC2 인스턴스에서 접근 가능하도록 설정

### 2. 보안 그룹 설정

EC2 인스턴스와 ElastiCache가 같은 보안 그룹에 있거나, ElastiCache 보안 그룹의 인바운드 규칙에서 EC2 보안 그룹의 6379 포트를 허용해야 합니다.

### 3. 인증 설정 (선택사항, 권장)

ElastiCache Redis 6.0 이상에서는 AUTH 토큰(비밀번호)을 설정할 수 있습니다:

1. ElastiCache 클러스터 생성 시 "Advanced Redis settings"에서 AUTH 토큰 설정
2. 또는 기존 클러스터 수정에서 AUTH 토큰 추가

### 4. 환경 변수 설정

프로덕션 환경 (EC2)의 `.env` 파일에 다음 설정 추가:

```env
# ElastiCache Redis 엔드포인트
REDIS_HOST=your-elasticache-endpoint.xxxxx.cache.amazonaws.com
REDIS_PORT=6379
REDIS_DB=0

# AUTH 토큰이 설정된 경우
REDIS_PASSWORD=your-auth-token

# 또는 환경 변수로 설정
export REDIS_HOST=your-elasticache-endpoint.xxxxx.cache.amazonaws.com
export REDIS_PORT=6379
export REDIS_PASSWORD=your-auth-token
```

### 5. ElastiCache 엔드포인트 확인

ElastiCache 콘솔에서 클러스터를 선택하면 Primary endpoint가 표시됩니다. 이 값을 `REDIS_HOST`에 사용합니다.

예시:
```
my-redis-cluster.abc123.0001.ap-northeast-2.cache.amazonaws.com
```

### 6. SSL/TLS 설정 (선택사항)

ElastiCache에서 전송 중 암호화가 활성화된 경우, `settings/base.py`의 Redis 설정에서 SSL 옵션을 활성화해야 합니다:

```python
# settings/base.py에서 주석 해제 및 수정
'OPTIONS': {
    'CLIENT_CLASS': 'django_redis.client.DefaultClient',
    'CONNECTION_POOL_KWARGS': {
        'ssl': True,
        'ssl_cert_reqs': None,
    },
},
```

## 사용 방법

### 패키지 설치

```bash
pip install -r requirements.txt
```

### 접속자 수 조회 API

#### 1. 전체 통계 조회

```bash
GET /api/visitors/stats/
```

응답:
```json
{
    "today": 150,
    "today_unique": 120,
    "total": 5000,
    "date": "2024-01-15"
}
```

#### 2. 상세 통계 조회

```bash
# 오늘 접속자 수
GET /api/visitors/detail/

# 특정 날짜 접속자 수
GET /api/visitors/detail/?date=2024-01-14
```

응답:
```json
{
    "today": 150,
    "total": 5000,
    "date": "2024-01-15"
}
```

### Python 코드에서 사용

```python
from main.utils import (
    get_today_visitors_count,
    get_total_visitors_count,
    get_visitor_stats,
    get_daily_visitors_count
)

# 오늘 접속자 수
today_count = get_today_visitors_count()

# 누적 접속자 수
total_count = get_total_visitors_count()

# 전체 통계
stats = get_visitor_stats()
# {'today': 150, 'today_unique': 120, 'total': 5000, 'date': '2024-01-15'}

# 특정 날짜 접속자 수
date_count = get_daily_visitors_count('2024-01-14')
```

## 동작 원리

1. **미들웨어**: 모든 요청에 대해 `VisitorCountMiddleware`가 실행되어 접속자 수를 증가시킵니다.
2. **Redis 키 구조**:
   - `visitors:today`: 오늘 접속자 수 (deprecated, 일별 키 사용)
   - `visitors:total`: 누적 접속자 수
   - `visitors:daily:YYYY-MM-DD`: 특정 날짜의 접속자 수
   - `visitors:set:YYYY-MM-DD`: 특정 날짜의 고유 접속자 IP 집합 (중복 제거용)
3. **중복 제거**: 같은 IP 주소는 하루에 한 번만 카운트됩니다 (세트 사용).

## 제외 경로 및 필터

다음 경로는 접속자 수 카운팅에서 제외됩니다:
- `/admin`
- `/static`
- `/media`
- `/favicon.ico`
- `/api/`
- `/health`, `/healthz`
- `/robots.txt`
- `/sitemap.xml`, `/sitemap`
- `/.well-known`
- `/__debug__`, `/debug`

### 추가 필터링

미들웨어는 다음을 자동으로 필터링합니다:

1. **User-Agent 필터링**: 봇, 크롤러, 헬스체크 도구 자동 제외
   - 검색엔진 봇 (bot, crawler, spider 등)
   - 헬스체크 도구 (HealthCheck, monitor, ping 등)
   - 모니터링 서비스 (UptimeRobot, Pingdom, StatusCake 등)
   - 자동화 도구 (curl, wget, python 등)
   - AWS ELB 헬스체크
   - Kubernetes 프로브

2. **IP 주소 필터링**: 내부 IP 자동 제외
   - localhost (127.x.x.x)
   - 사설 IP 대역 (10.x.x.x, 172.16-31.x.x, 192.168.x.x)
   - 링크 로컬 (169.254.x.x)

제외 경로를 추가하려면 `main/middleware.py`의 `VisitorCountMiddleware.EXCLUDED_PATHS` 리스트를 수정하세요.
User-Agent 패턴을 추가하려면 `EXCLUDED_USER_AGENTS` 리스트를 수정하세요.

## 문제 해결

### Redis 연결 실패

1. Redis 서버가 실행 중인지 확인:
   ```bash
   redis-cli ping
   # 응답: PONG
   ```

2. 호스트 및 포트 확인:
   ```bash
   redis-cli -h your-host -p 6379 ping
   ```

3. 방화벽/보안 그룹 확인 (ElastiCache의 경우)

### ElastiCache 연결 실패

1. **보안 그룹 확인**: EC2 인스턴스와 ElastiCache가 같은 VPC에 있고, 보안 그룹이 올바르게 설정되어 있는지 확인

2. **엔드포인트 확인**: ElastiCache 콘솔에서 정확한 Primary endpoint 확인

3. **AUTH 토큰 확인**: 비밀번호가 설정된 경우 `REDIS_PASSWORD` 환경 변수 확인

4. **VPC 설정 확인**: EC2와 ElastiCache가 같은 서브넷 그룹에 있어야 함 (또는 라우팅 가능)

### 접속자 수가 증가하지 않는 경우

1. 미들웨어가 `settings/base.py`의 `MIDDLEWARE` 리스트에 포함되어 있는지 확인
2. Redis 연결 상태 확인
3. 로그 파일 확인: `logs/django.log` (프로덕션 환경)

## 성능 고려사항

- Redis는 메모리 기반이므로 매우 빠른 성능을 제공합니다
- 일별 키는 30일 후 자동 만료되도록 설정되어 있습니다
- 대량의 트래픽이 예상되는 경우 Redis 연결 풀 크기를 조정할 수 있습니다 (`settings/base.py`에서 `max_connections` 수정)

## Redis 연결 수 최적화

EC2에서 별도로 구축한 Redis 서버의 접속자 수(연결 수)를 줄이기 위한 최적화:

### 1. 미들웨어 필터링 강화
- 봇, 헬스체크, 모니터링 도구 자동 제외
- 내부 IP 주소 자동 제외
- 불필요한 경로 제외 (robots.txt, sitemap.xml 등)

### 2. Redis 연결 풀 최적화
- `max_connections`: 연결 풀 최대 크기 제한 (기본: 50)
- `socket_keepalive`: TCP keepalive로 불필요한 재연결 방지
- 연결 재사용 최적화

### 3. Celery 연결 최적화
- `CELERY_BROKER_POOL_LIMIT`: 브로커 연결 풀 크기 제한 (기본: 10)
- `CELERY_RESULT_EXPIRES`: 결과 TTL 설정으로 메모리 절약 (기본: 3600초)
- Worker 프로세스 최적화 설정

### 4. Redis 연결 수 확인 방법

Redis 서버에서 현재 연결 수 확인:
```bash
redis-cli -h your-redis-host -p 6379 INFO clients
# 또는
redis-cli -h your-redis-host -p 6379 CLIENT LIST | wc -l
```

일반적으로 다음 프로세스들이 Redis에 연결합니다:
- Gunicorn 워커 프로세스 수 × 연결 풀 크기
- Celery Worker 프로세스
- Celery Beat 프로세스
- Django 애플리케이션 (캐시 및 접속자 수 추적)

### 5. 연결 수가 많은 경우 체크리스트

1. **Gunicorn 워커 수 확인**: 워커가 많을수록 연결 수 증가
   ```bash
   ps aux | grep gunicorn
   ```

2. **Celery 프로세스 확인**: 불필요한 Worker/Beat 프로세스가 있는지 확인
   ```bash
   ps aux | grep celery
   supervisorctl status celery_worker celery_beat
   ```

3. **연결 풀 크기 조정**: `settings/base.py`에서 `max_connections` 값 감소 고려

4. **봇/헬스체크 요청 확인**: 로그에서 실제 사용자 요청인지 확인
   ```bash
   tail -f logs/django.log | grep "접속자 수"
   ```

## 비용 최적화 (AWS ElastiCache)

- **프리 티어**: `cache.t3.micro` 노드 타입 사용 시 750시간/월 무료 (12개월)
- **예약 인스턴스**: 장기 사용 시 예약 인스턴스로 최대 55% 절감
- **노드 타입 선택**: 트래픽에 맞는 적절한 노드 타입 선택
- **자동 백업 비활성화**: 필요 없는 경우 자동 백업 비활성화로 비용 절감

