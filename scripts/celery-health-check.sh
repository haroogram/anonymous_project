#!/bin/bash
# Celery & Celery Beat 헬스체크 스크립트
# 사용법: ./scripts/celery-health-check.sh

set -e

# 색상 코드
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 프로젝트 디렉토리 설정
PROJECT_DIR="${PROJECT_DIR:-/home/ubuntu/anonymous_project}"
VENV_DIR="${VENV_DIR:-/home/ubuntu/venv}"

echo "=========================================="
echo "Celery & Celery Beat 헬스체크"
echo "=========================================="
echo ""

# 1. Redis 연결 확인
echo "1. Redis 연결 확인:"

# 환경 변수에서 Redis 설정 읽기 (.env 파일이 있으면 로드)
if [ -f "${PROJECT_DIR}/.env" ]; then
    set -a
    source "${PROJECT_DIR}/.env"
    set +a
fi

# Redis 연결 정보 설정 (환경 변수 또는 기본값)
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"
REDIS_PASSWORD="${REDIS_PASSWORD:-}"

echo "   Redis 호스트: ${REDIS_HOST}:${REDIS_PORT}"

# redis-cli 명령어 구성
REDIS_CLI_CMD="redis-cli -h ${REDIS_HOST} -p ${REDIS_PORT}"

# 비밀번호가 있으면 추가
if [ -n "$REDIS_PASSWORD" ]; then
    REDIS_CLI_CMD="${REDIS_CLI_CMD} -a ${REDIS_PASSWORD}"
fi

# Redis 연결 테스트
if $REDIS_CLI_CMD ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis 연결 성공${NC}"
    $REDIS_CLI_CMD ping
else
    echo -e "${RED}✗ Redis 연결 실패${NC}"
    echo "   Redis 서버가 실행 중인지 확인하세요: $REDIS_CLI_CMD ping"
    echo "   환경 변수 확인: REDIS_HOST=${REDIS_HOST}, REDIS_PORT=${REDIS_PORT}"
fi
echo ""

# 2. Supervisor 프로세스 상태 확인 (먼저 확인)
echo "2. Supervisor 프로세스 상태:"
WORKER_RUNNING=false
BEAT_RUNNING=false

if command -v supervisorctl > /dev/null 2>&1; then
    # Supervisor 상태 확인
    WORKER_STATUS=$(sudo supervisorctl status celery_worker 2>/dev/null | awk '{print $2}' || echo "")
    BEAT_STATUS=$(sudo supervisorctl status celery_beat 2>/dev/null | awk '{print $2}' || echo "")
    
    # 전체 상태 출력
    sudo supervisorctl status celery_worker celery_beat 2>/dev/null || echo "Supervisor 서비스를 확인할 수 없습니다"
    
    # 상태 파싱
    if [ "$WORKER_STATUS" = "RUNNING" ]; then
        WORKER_RUNNING=true
        echo -e "   ${GREEN}✓ Celery Worker 프로세스 실행 중${NC}"
    else
        echo -e "   ${RED}✗ Celery Worker 프로세스가 실행 중이 아닙니다 (상태: ${WORKER_STATUS:-UNKNOWN})${NC}"
    fi
    
    if [ "$BEAT_STATUS" = "RUNNING" ]; then
        BEAT_RUNNING=true
        echo -e "   ${GREEN}✓ Celery Beat 프로세스 실행 중${NC}"
    else
        echo -e "   ${RED}✗ Celery Beat 프로세스가 실행 중이 아닙니다 (상태: ${BEAT_STATUS:-UNKNOWN})${NC}"
    fi
else
    echo -e "${YELLOW}⚠ supervisorctl 명령어를 찾을 수 없습니다${NC}"
fi
echo ""

# 3. Celery Worker 연결 확인 (프로세스가 실행 중일 때만)
echo "3. Celery Worker 연결 확인:"
if [ "$WORKER_RUNNING" = true ]; then
    if [ -f "${VENV_DIR}/bin/celery" ]; then
        cd "${PROJECT_DIR}"
        # 환경 변수 로드 (이미 위에서 로드했지만 확실히 하기 위해)
        if [ -f "${PROJECT_DIR}/.env" ]; then
            set -a
            source "${PROJECT_DIR}/.env"
            set +a
        fi
        
        if DJANGO_SETTINGS_MODULE=anonymous_project.settings.production ${VENV_DIR}/bin/celery -A anonymous_project.celery:app inspect ping > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Celery Worker 연결 성공 (Redis 브로커 응답 정상)${NC}"
            DJANGO_SETTINGS_MODULE=anonymous_project.settings.production ${VENV_DIR}/bin/celery -A anonymous_project.celery:app inspect ping
        else
            echo -e "${RED}✗ Celery Worker 연결 실패${NC}"
            echo "   프로세스는 실행 중이지만 Redis 브로커에 연결할 수 없습니다."
            echo "   Redis 연결 상태와 Worker 로그를 확인하세요."
        fi
    else
        echo -e "${YELLOW}⚠ Celery 명령어를 찾을 수 없습니다. 가상환경 경로를 확인하세요.${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Celery Worker 프로세스가 실행 중이 아니므로 연결 확인을 건너뜁니다.${NC}"
    echo "   먼저 Worker를 시작하세요: sudo supervisorctl start celery_worker"
fi
echo ""

# 4. 등록된 작업 확인
echo "4. 등록된 작업 목록:"
if [ -f "${VENV_DIR}/bin/celery" ]; then
    cd "${PROJECT_DIR}"
    DJANGO_SETTINGS_MODULE=anonymous_project.settings.production ${VENV_DIR}/bin/celery -A anonymous_project.celery:app inspect registered 2>/dev/null | head -30 || echo "작업 목록을 가져올 수 없습니다"
else
    echo "Celery 명령어를 찾을 수 없습니다"
fi
echo ""

# 5. 활성 작업 확인
echo "5. 현재 활성 작업:"
if [ -f "${VENV_DIR}/bin/celery" ]; then
    cd "${PROJECT_DIR}"
    ACTIVE_TASKS=$(DJANGO_SETTINGS_MODULE=anonymous_project.settings.production ${VENV_DIR}/bin/celery -A anonymous_project.celery:app inspect active 2>/dev/null)
    if [ -z "$ACTIVE_TASKS" ] || echo "$ACTIVE_TASKS" | grep -q "No nodes"; then
        echo -e "${GREEN}✓ 현재 활성 작업 없음 (정상)${NC}"
    else
        echo "$ACTIVE_TASKS"
    fi
else
    echo "Celery 명령어를 찾을 수 없습니다"
fi
echo ""

# 6. 로그 파일 확인
echo "6. 최근 로그 확인:"
WORKER_LOG="${PROJECT_DIR}/logs/celery_worker.log"
BEAT_LOG="${PROJECT_DIR}/logs/celery_beat.log"

if [ -f "$WORKER_LOG" ]; then
    echo "Celery Worker 로그 (마지막 5줄):"
    tail -n 5 "$WORKER_LOG" 2>/dev/null || echo "로그를 읽을 수 없습니다"
else
    echo -e "${YELLOW}⚠ Worker 로그 파일을 찾을 수 없습니다: $WORKER_LOG${NC}"
fi
echo ""

if [ -f "$BEAT_LOG" ]; then
    echo "Celery Beat 로그 (마지막 5줄):"
    tail -n 5 "$BEAT_LOG" 2>/dev/null || echo "로그를 읽을 수 없습니다"
else
    echo -e "${YELLOW}⚠ Beat 로그 파일을 찾을 수 없습니다: $BEAT_LOG${NC}"
fi
echo ""

# 7. 에러 로그 확인
echo "7. 최근 에러 확인 (로그에서 'ERROR' 키워드):"
if [ -f "$WORKER_LOG" ]; then
    ERRORS=$(grep -i "error" "$WORKER_LOG" 2>/dev/null | tail -n 3)
    if [ -z "$ERRORS" ]; then
        echo -e "${GREEN}✓ 최근 에러 없음${NC}"
    else
        echo -e "${RED}⚠ 최근 에러 발견:${NC}"
        echo "$ERRORS"
    fi
else
    echo "로그 파일을 찾을 수 없습니다"
fi
echo ""

# 8. 요약
echo "=========================================="
echo "요약"
echo "=========================================="
echo ""
echo "상태 확인 명령어:"
echo "  - Supervisor 상태: sudo supervisorctl status"
echo "  - Worker 로그: tail -f $WORKER_LOG"
echo "  - Beat 로그: tail -f $BEAT_LOG"
echo "  - 작업 수동 실행: python manage.py shell"
echo "    >>> from main.tasks import sync_visitor_stats_task"
echo "    >>> sync_visitor_stats_task.delay()"
echo ""
echo "자세한 내용은 CELERY_MONITORING.md 문서를 참조하세요."

