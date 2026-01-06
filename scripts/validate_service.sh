#!/bin/bash

# ValidateService 스크립트
# 서비스가 정상적으로 실행 중인지 확인

set -e  # 에러 발생 시 스크립트 중단

echo "================================"
echo "ValidateService 시작"
echo "================================"

APP_DIR="/home/ubuntu/anonymous_project"
MAX_RETRIES=5
RETRY_INTERVAL=10

# Health check 함수 (개선)
check_health() {
    local url="http://localhost:8000"
    # 연결 타임아웃 설정 (5초)
    local response_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 --connect-timeout 5 $url 2>/dev/null || echo "000")
    
    if [ "$response_code" -eq 200 ] || [ "$response_code" -eq 301 ] || [ "$response_code" -eq 302 ]; then
        echo "✅ Health check 성공: HTTP $response_code"
        return 0
    else
        echo "❌ Health check 실패: HTTP $response_code"
        # 디버깅 정보 출력
        echo "   포트 8000 리스닝 상태:"
        netstat -tuln 2>/dev/null | grep ":8000 " || ss -tuln 2>/dev/null | grep ":8000 " || echo "   포트 8000이 리스닝하지 않음"
        echo "   Supervisor 상태:"
        supervisorctl status anonymous_project 2>/dev/null || echo "   Supervisor 상태 확인 실패"
        return 1
    fi
}

# 프로세스 확인
check_process() {
    # Supervisor를 사용하는 경우 (우선 확인)
    if command -v supervisorctl &> /dev/null; then
        local status=$(supervisorctl status anonymous_project 2>/dev/null || echo "")
        if echo "$status" | grep -q "RUNNING"; then
            echo "✅ Supervisor로 관리되는 애플리케이션 실행 중"
            # 포트가 실제로 리스닝하는지 확인
            if netstat -tuln 2>/dev/null | grep -q ":8000 " || ss -tuln 2>/dev/null | grep -q ":8000 "; then
                echo "✅ 포트 8000 리스닝 확인"
                return 0
            else
                echo "⚠️  Supervisor는 실행 중이지만 포트 8000이 아직 리스닝하지 않음"
                return 1
            fi
        else
            echo "❌ Supervisor 프로그램이 실행 중이 아닙니다: $status"
            return 1
        fi
    fi
    
    # Gunicorn 프로세스 확인 (fallback)
    if pgrep -f "gunicorn" > /dev/null; then
        echo "✅ Gunicorn 프로세스 실행 중"
        # 포트 확인
        if netstat -tuln 2>/dev/null | grep -q ":8000 " || ss -tuln 2>/dev/null | grep -q ":8000 "; then
            echo "✅ 포트 8000 리스닝 확인"
            return 0
        else
            echo "⚠️  Gunicorn 프로세스는 있지만 포트 8000이 리스닝하지 않음"
            return 1
        fi
    fi
    
    # systemd를 사용하는 경우
    if systemctl is-active --quiet anonymous_project.service 2>/dev/null; then
        echo "✅ systemd 서비스 실행 중"
        return 0
    fi
    
    echo "❌ 애플리케이션 프로세스를 찾을 수 없습니다"
    return 1
}

# 재시도 로직
retry_count=0
while [ $retry_count -lt $MAX_RETRIES ]; do
    echo "Health check 시도 $((retry_count + 1))/$MAX_RETRIES"
    
    if check_process && check_health; then
        echo "================================"
        echo "✅ ValidateService 성공"
        echo "================================"
        exit 0
    fi
    
    retry_count=$((retry_count + 1))
    
    if [ $retry_count -lt $MAX_RETRIES ]; then
        echo "$RETRY_INTERVAL초 후 재시도..."
        sleep $RETRY_INTERVAL
    fi
done

echo "================================"
echo "❌ ValidateService 실패: 최대 재시도 횟수 초과"
echo "================================"
exit 1

