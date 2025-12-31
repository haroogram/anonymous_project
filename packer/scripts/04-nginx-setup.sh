#!/bin/bash
set -e

echo "================================"
echo "[4/8] Nginx 설치 및 설정"
echo "================================"

# Nginx 설치
# 참고: apt-get update는 01-base-setup.sh에서 이미 실행됨
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y nginx

# Nginx 기본 설정 백업
if [ -f /etc/nginx/sites-available/default ]; then
    sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup
fi

# Nginx 설정 파일 생성 (기본 템플릿, 실제 설정은 배포 시 적용)
sudo tee /etc/nginx/sites-available/anonymous_project > /dev/null <<EOF
# Django 애플리케이션을 위한 Nginx 설정
# 실제 배포 시 도메인 및 경로를 수정해야 합니다

upstream django {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name _;

    client_max_body_size 100M;

    # Static files
    location /static/ {
        alias /home/ubuntu/anonymous/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files (필요한 경우)
    # location /media/ {
    #     alias /home/ubuntu/anonymous/media/;
    #     expires 30d;
    # }

    # Django 애플리케이션
    location / {
        proxy_pass http://django;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

# 사이트 활성화 (디폴트 비활성화)
sudo ln -sf /etc/nginx/sites-available/anonymous_project /etc/nginx/sites-enabled/anonymous_project
sudo rm -f /etc/nginx/sites-enabled/default

# Nginx 설정 테스트
sudo nginx -t

# Nginx 중지 (AMI에서는 시작하지 않음)
sudo systemctl stop nginx || true
sudo systemctl disable nginx || true

echo "✅ Nginx 설치 및 기본 설정 완료"

