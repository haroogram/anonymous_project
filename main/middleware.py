"""
접속자 수 추적 및 /admin IP 제한 미들웨어
"""
import logging
import re
from django.conf import settings
from django.http import HttpResponseForbidden
from .utils import increment_visitor_count, get_client_ip

logger = logging.getLogger(__name__)


class AdminIPRestrictionMiddleware:
    """
    /admin 경로에 대한 IP 화이트리스트 미들웨어
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # 허용 IP는 환경 변수(SSM -> .env -> settings)로 주입합니다.
        self.allowed_ips = getattr(
            settings,
            "ADMIN_ALLOWED_IPS",
            [],
        )

    def __call__(self, request):
        path = request.path or ""
        if path.startswith("/admin"):
            client_ip = get_client_ip(request)
            if client_ip not in self.allowed_ips:
                logger.warning(
                    "[AdminIPRestriction] blocked path=%s ip=%s", path, client_ip
                )
                return HttpResponseForbidden("Forbidden")
        return self.get_response(request)


class VisitorCountMiddleware:
    """
    접속자 수를 추적하는 미들웨어
    
    특정 경로와 봇/헬스체크 요청은 제외할 수 있습니다.
    """
    
    # 접속자 수 카운팅에서 제외할 경로
    EXCLUDED_PATHS = [
        '/admin',
        '/static',
        '/media',
        '/favicon.ico',
        '/api/',
        '/health',
        '/healthz',
        '/robots.txt',
        '/sitemap.xml',
        '/sitemap',
        '/.well-known',
        '/__debug__',
        '/debug',
        '/errors/',
    ]
    
    # 제외할 User-Agent 패턴 (봇, 헬스체크, 모니터링 도구 등)
    EXCLUDED_USER_AGENTS = [
        r'bot', r'crawler', r'spider', r'scanner', r'crawl',  # 검색엔진 봇
        r'HealthCheck', r'health', r'monitor', r'ping',  # 헬스체크
        r'UptimeRobot', r'Pingdom', r'StatusCake', r'NewRelic',  # 모니터링 서비스
        r'curl', r'wget', r'python', r'go-http', r'java',  # 자동화 도구
        r'Amazon-Route53', r'AlwaysOn', r'AlwaysOnHealthCheck',  # AWS 관련
        r'ELB-HealthChecker', r'ELB-HealthChecker/',  # AWS ELB 헬스체크
        r'kube-probe', r'kubelet',  # Kubernetes 헬스체크
        r'Zabbix', r'Nagios', r'Prometheus',  # 모니터링 도구
        r'^$',  # 빈 User-Agent
    ]
    
    # 제외할 IP 주소 패턴 (내부 IP, 로드밸런서 등)
    EXCLUDED_IP_PATTERNS = [
        r'^127\.',  # localhost
        r'^10\.',  # 사설 IP (10.x.x.x)
        r'^172\.(1[6-9]|2[0-9]|3[0-1])\.',  # 사설 IP (172.16-31.x.x)
        r'^192\.168\.',  # 사설 IP (192.168.x.x)
        r'^169\.254\.',  # 링크 로컬
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
        # User-Agent 패턴 컴파일 (성능 최적화)
        self._ua_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.EXCLUDED_USER_AGENTS]
        # IP 패턴 컴파일
        self._ip_patterns = [re.compile(pattern) for pattern in self.EXCLUDED_IP_PATTERNS]
    
    def __call__(self, request):
        # 요청 정보 로깅 (실제 IP / 헤더 확인용)
        ip_address = get_client_ip(request)
        xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
        remote_addr = request.META.get('REMOTE_ADDR', '')
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # k3s/ALB health check 등은 로깅에서 제외
        path = request.path or ""
        if not (path.startswith('/healthz') or 'kube-probe' in user_agent):
            logger.info(
                "[VisitorCountMiddleware] path=%s ip=%s xff=%s remote_addr=%s ua=%s",
                path,
                ip_address,
                xff,
                remote_addr,
                user_agent,
            )

        # 접속자 수 카운팅 (제외 조건 체크)
        if not self._should_exclude(request):
            try:
                # 접속자 수 증가
                increment_visitor_count(ip_address=ip_address, user_agent=user_agent)
            except Exception as e:
                # 접속자 수 카운팅 실패해도 요청은 계속 진행
                logger.warning(f"접속자 수 카운팅 실패: {e}")
        
        response = self.get_response(request)
        return response
    
    def _should_exclude(self, request):
        """
        해당 요청이 카운팅에서 제외되어야 하는지 확인
        
        Args:
            request: Django request 객체
            
        Returns:
            bool: 제외해야 하면 True
        """
        # 경로 / User-Agent 확인
        path = request.path or ""
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # 헬스체크 관련 요청은 로깅 없이 바로 제외 처리
        if path.startswith('/healthz') or path.startswith('/health') or 'kube-probe' in user_agent:
            return True

        # 경로 확인
        for excluded_path in self.EXCLUDED_PATHS:
            if path.startswith(excluded_path):
                logger.info(
                    "[VisitorCountMiddleware] exclude=True reason=path path=%s pattern=%s",
                    path,
                    excluded_path,
                )
                return True
        
        # User-Agent 확인
        for pattern in self._ua_patterns:
            if pattern.search(user_agent):
                logger.info(
                    "[VisitorCountMiddleware] exclude=True reason=user_agent ua=%s pattern=%s",
                    user_agent,
                    pattern.pattern,
                )
                return True
        
        # IP 주소 확인
        ip_address = get_client_ip(request)
        for pattern in self._ip_patterns:
            if pattern.match(ip_address):
                logger.info(
                    "[VisitorCountMiddleware] exclude=True reason=ip ip=%s pattern=%s",
                    ip_address,
                    pattern.pattern,
                )
                return True

        logger.info(
            "[VisitorCountMiddleware] exclude=False path=%s ip=%s ua=%s",
            path,
            ip_address,
            user_agent,
        )
        return False

