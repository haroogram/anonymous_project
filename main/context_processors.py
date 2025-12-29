"""
템플릿 context processor - 모든 템플릿에서 접속자 통계 사용 가능
"""
from .utils import get_today_unique_visitors_count, get_total_visitors_count


def visitor_stats(request):
    """
    모든 템플릿에서 접속자 통계를 사용할 수 있도록 context에 추가
    """
    return {
        'today_visitors': get_today_unique_visitors_count(),
        'total_visitors': get_total_visitors_count(),
    }

