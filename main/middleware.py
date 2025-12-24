"""
접속자 수 추적 미들웨어
모든 요청에 대해 접속자 수를 카운팅합니다.
"""
import logging
from .utils import increment_visitor_count

logger = logging.getLogger(__name__)


class VisitorCountMiddleware:
    """
    접속자 수를 추적하는 미들웨어
    
    특정 경로는 제외할 수 있습니다 (예: /admin, /static, /media 등)
    """
    
    # 접속자 수 카운팅에서 제외할 경로
    EXCLUDED_PATHS = [
        '/admin',
        '/static',
        '/media',
        '/favicon.ico',
        '/api/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 접속자 수 카운팅 (제외 경로가 아닌 경우만)
        if not self._should_exclude(request.path):
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
    
    def _should_exclude(self, path):
        """
        해당 경로가 카운팅에서 제외되어야 하는지 확인
        
        Args:
            path: 요청 경로
            
        Returns:
            bool: 제외해야 하면 True
        """
        for excluded_path in self.EXCLUDED_PATHS:
            if path.startswith(excluded_path):
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

