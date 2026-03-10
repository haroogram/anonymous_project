#!/bin/bash

# ApplicationStop 스크립트
# 애플리케이션 종료 (Supervisor 사용)

set -e  # 에러 발생 시 스크립트 중단

echo "================================"
echo "ApplicationStop 시작"
echo "================================"

# Supervisor를 사용하는 경우
if command -v supervisorctl &> /dev/null; then
    echo "Supervisor로 애플리케이션 중지 중..."
    
    # Supervisor 서비스 상태 확인
    if ! sudo systemctl is-active --quiet supervisor 2>/dev/null; then
        echo "⚠️  Supervisor 서비스가 실행 중이 아닙니다."
    fi
    
    # anonymous_project 중지
    echo "anonymous_project 중지 중..."
    status=$(sudo supervisorctl status anonymous_project 2>/dev/null || echo "")
    if echo "$status" | grep -q "RUNNING"; then
        echo "서비스 상태: $status"
        timeout 30 sudo supervisorctl stop anonymous_project 2>&1 || {
            EXIT_CODE=$?
            if [ $EXIT_CODE -eq 124 ]; then
                echo "⚠️  anonymous_project 중지 타임아웃 발생 (30초 초과)"
            else
                echo "⚠️  anonymous_project 중지 실패 (종료 코드: $EXIT_CODE)"
            fi
        }
        
        # 중지 확인
        sleep 1
        final_status=$(sudo supervisorctl status anonymous_project 2>/dev/null || echo "")
        if echo "$final_status" | grep -q "RUNNING"; then
            echo "⚠️  anonymous_project가 여전히 실행 중입니다. 강제 종료 시도..."
            sudo supervisorctl stop anonymous_project || true
        else
            echo "✅ anonymous_project가 성공적으로 중지되었습니다."
        fi
    else
        echo "anonymous_project가 실행 중이 아닙니다: $status"
    fi
    
    # Celery Worker 중지
    echo "celery_worker 중지 중..."
    status=$(sudo supervisorctl status celery_worker 2>/dev/null || echo "")
    if echo "$status" | grep -q "RUNNING"; then
        timeout 30 sudo supervisorctl stop celery_worker 2>&1 || {
            EXIT_CODE=$?
            if [ $EXIT_CODE -eq 124 ]; then
                echo "⚠️  celery_worker 중지 타임아웃 발생 (30초 초과)"
            else
                echo "⚠️  celery_worker 중지 실패 (종료 코드: $EXIT_CODE)"
            fi
        }
    else
        echo "celery_worker가 실행 중이 아닙니다: $status"
    fi
    
    # Celery Beat 중지
    echo "celery_beat 중지 중..."
    status=$(sudo supervisorctl status celery_beat 2>/dev/null || echo "")
    if echo "$status" | grep -q "RUNNING"; then
        timeout 30 sudo supervisorctl stop celery_beat 2>&1 || {
            EXIT_CODE=$?
            if [ $EXIT_CODE -eq 124 ]; then
                echo "⚠️  celery_beat 중지 타임아웃 발생 (30초 초과)"
            else
                echo "⚠️  celery_beat 중지 실패 (종료 코드: $EXIT_CODE)"
            fi
        }
    else
        echo "celery_beat가 실행 중이 아닙니다: $status"
    fi
    
    echo "✅ Supervisor를 통한 애플리케이션 중지 완료"
else
    echo "⚠️  supervisorctl을 찾을 수 없습니다. Supervisor가 설치되어 있지 않을 수 있습니다."
fi

# Fallback: Supervisor로 관리되지 않는 프로세스 직접 종료
# (Supervisor가 실패했거나 프로세스가 Supervisor 밖에서 실행된 경우)
echo "Fallback: Supervisor로 관리되지 않는 프로세스 확인 중..."

# Gunicorn 프로세스 직접 종료 (fallback)
if pgrep -f "gunicorn" > /dev/null; then
    echo "⚠️  Supervisor로 관리되지 않는 Gunicorn 프로세스 발견. 직접 종료 중..."
    pkill -f gunicorn || true
    sleep 2
    
    # 강제 종료 (필요한 경우)
    if pgrep -f "gunicorn" > /dev/null; then
        echo "⚠️  Gunicorn 프로세스가 여전히 실행 중입니다. 강제 종료 시도..."
        pkill -9 -f gunicorn || true
    else
        echo "✅ Gunicorn 프로세스 종료 완료"
    fi
fi

# Celery 프로세스 종료 (fallback)
if pgrep -f "celery" > /dev/null; then
    echo "⚠️  Supervisor로 관리되지 않는 Celery 프로세스 발견. 직접 종료 중..."
    pkill -f "celery worker" || true
    pkill -f "celery beat" || true
    sleep 2
    
    # 강제 종료 (필요한 경우)
    if pgrep -f "celery" > /dev/null; then
        echo "⚠️  Celery 프로세스가 여전히 실행 중입니다. 강제 종료 시도..."
        pkill -9 -f "celery" || true
    else
        echo "✅ Celery 프로세스 종료 완료"
    fi
fi

echo "ApplicationStop 완료"

