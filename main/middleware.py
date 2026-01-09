"""
접속자 수 추적 미들웨어
모든 요청에 대해 접속자 수를 카운팅합니다.
"""
import logging
import re
from .utils import increment_visitor_count

logger = logging.getLogger(__name__)


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
        # 접속자 수 카운팅 (제외 조건 체크)
        if not self._should_exclude(request):
            try:
                # IP 주소 가져오기 (프록시 뒤에 있는 경우 X-Forwarded-For 헤더 확인)
                ip_address = self._get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                
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
        # 경로 확인
        path = request.path
        for excluded_path in self.EXCLUDED_PATHS:
            if path.startswith(excluded_path):
                return True
        
        # User-Agent 확인
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        for pattern in self._ua_patterns:
            if pattern.search(user_agent):
                return True
        
        # IP 주소 확인
        ip_address = self._get_client_ip(request)
        for pattern in self._ip_patterns:
            if pattern.match(ip_address):
                return True
        
        return False
    
    def _get_client_ip(self, request):
        """
        클라이언트의 실제 IP 주소를 가져옵니다.
        
        프록시나 로드 밸런서를 통한 경우 X-Forwarded-For 헤더를 확인합니다.
        
        Args:
            request: Django request 객체
            
        Returns:
            str: IP 주소
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # X-Forwarded-For 헤더는 여러 IP를 포함할 수 있음 (예: "client, proxy1, proxy2")
            # 첫 번째 IP가 실제 클라이언트 IP
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip

