# 배포 로그 확인 가이드

## CodeDeploy 로그 위치

배포 중 문제가 발생했을 때 다음 로그 파일들을 확인하세요:

### 1. CodeDeploy Agent 로그
```bash
# CodeDeploy 에이전트 메인 로그
sudo tail -f /opt/codedeploy-agent/deployment-root/deployment-logs/codedeploy-agent.log

# 또는 최근 로그만 확인
sudo tail -n 100 /opt/codedeploy-agent/deployment-root/deployment-logs/codedeploy-agent.log
```

### 2. 배포별 스크립트 로그
```bash
# 최근 배포 디렉토리 찾기
LATEST_DEPLOY=$(ls -t /opt/codedeploy-agent/deployment-root | head -1)
echo "최근 배포 ID: $LATEST_DEPLOY"

# 스크립트 실행 로그 확인
sudo tail -f /opt/codedeploy-agent/deployment-root/$LATEST_DEPLOY/logs/scripts.log

# 또는 최근 로그만 확인
sudo tail -n 200 /opt/codedeploy-agent/deployment-root/$LATEST_DEPLOY/logs/scripts.log
```

### 3. ApplicationStop 스크립트 상세 로그
```bash
# stderr와 stdout 모두 확인
sudo tail -n 200 /opt/codedeploy-agent/deployment-root/$LATEST_DEPLOY/logs/scripts.log | grep -A 50 "ApplicationStop"
```

### 4. Systemd 서비스 로그
```bash
# anonymous_project 서비스 로그
sudo journalctl -u anonymous_project.service -n 50 --no-pager

# 실시간 로그 모니터링
sudo journalctl -u anonymous_project.service -f

# systemd 전체 로그
sudo journalctl -n 100 --no-pager
```

### 5. Supervisor 로그 (사용하는 경우)
```bash
# Supervisor 메인 로그
sudo tail -f /var/log/supervisor/supervisord.log

# 애플리케이션별 로그
sudo tail -f /var/log/supervisor/anonymous_project.log
sudo tail -f /var/log/supervisor/celery_worker.log
```

## 문제 진단 방법

### ApplicationStop에서 멈춘 경우

1. **SSH로 서버 접속 후 확인:**
```bash
# 서비스 상태 확인
sudo systemctl status anonymous_project.service

# 프로세스 확인
ps aux | grep gunicorn
ps aux | grep celery

# systemd가 멈춰있는지 확인
sudo systemctl list-jobs
```

2. **수동으로 서비스 중지 시도:**
```bash
# 일반 중지
sudo systemctl stop anonymous_project.service

# 타임아웃 발생 시 강제 종료
sudo systemctl kill --signal=SIGKILL anonymous_project.service

# 프로세스 직접 종료
sudo pkill -9 -f gunicorn
sudo pkill -9 -f celery
```

3. **CodeDeploy 에이전트 재시작:**
```bash
sudo service codedeploy-agent restart
```

### 로그에서 확인할 사항

1. **타임아웃 확인:**
   - `appspec.yml`에서 ApplicationStop 타임아웃은 300초입니다
   - `systemctl stop` 명령이 30초 이상 걸리면 타임아웃됩니다

2. **권한 문제 확인:**
   - `sudo` 권한이 있는지 확인
   - `/etc/sudoers`에서 ubuntu 사용자 권한 확인

3. **서비스 상태 확인:**
   - 서비스가 실제로 실행 중인지
   - 서비스가 멈춰있는지 (hung 상태)

## 빠른 문제 해결

배포가 멈췄을 때 즉시 확인할 명령어:

```bash
# 1. 최근 배포 로그 확인
sudo tail -n 100 /opt/codedeploy-agent/deployment-root/$(ls -t /opt/codedeploy-agent/deployment-root | head -1)/logs/scripts.log

# 2. 서비스 상태 확인
sudo systemctl status anonymous_project.service

# 3. 프로세스 확인
ps aux | grep -E "gunicorn|celery|python.*manage.py"

# 4. systemd 작업 확인
sudo systemctl list-jobs

# 5. CodeDeploy 에이전트 상태
sudo service codedeploy-agent status
```

## 개선된 스크립트의 변경사항

`application_stop.sh`에 다음 개선사항이 추가되었습니다:

1. **상세한 로깅**: 각 단계마다 로그 출력
2. **타임아웃 설정**: `systemctl stop` 명령에 30초 타임아웃
3. **에러 처리**: 실패 시에도 계속 진행하되 경고 메시지 출력
4. **상태 확인**: 중지 후 서비스 상태 재확인
5. **강제 종료**: 필요 시 SIGKILL로 강제 종료

이제 배포 로그에서 더 자세한 정보를 확인할 수 있습니다.
