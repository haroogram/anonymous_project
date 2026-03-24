# Python 3.12 slim 이미지 사용
FROM python:3.12-slim

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=anonymous_project.settings.production

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치 (MariaDB 클라이언트, AWS CLI 포함)
RUN apt update && apt install -y --no-install-recommends \
    gcc \
    libmariadb-dev \
    pkg-config \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# AWS CLI v2 설치 (SSM Parameter Store 사용 시 필요)
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip -q awscliv2.zip \
    && ./aws/install \
    && rm -rf awscliv2.zip aws/

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 엔트리포인트 스크립트: CRLF → LF 변환 및 실행 권한 부여
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# 로그 디렉토리 생성
RUN mkdir -p /app/logs

# 정적 파일·미디어(업로드) 디렉토리 생성
RUN mkdir -p /app/staticfiles /app/media

# 비루트 사용자 생성 및 권한 설정
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

# 포트 노출
EXPOSE 8000

# 헬스체크 (시작 시간 여유 확보 - migrate 실행 시간 고려)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/')" || exit 1

# 엔트리포인트 스크립트로 실행 (migrate → load_initial_data → gunicorn)
ENTRYPOINT ["/app/entrypoint.sh"]
