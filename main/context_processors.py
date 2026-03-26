"""
템플릿 context processor - 모든 템플릿에서 접속자 통계 사용 가능
"""
from .models import BoardNotification
from .utils import get_today_unique_visitors_count, get_total_visitors_count


# 로드 시 토스트로 보여 줄 미읽음 알림 최대 개수 (배지 숫자와 별개)
BOARD_NOTIFICATION_TOAST_LIMIT = 5


def notification_badge(request):
    if not request.user.is_authenticated:
        return {
            "unread_board_notification_count": 0,
            "unread_board_notification_toasts": [],
        }
    unread_qs = BoardNotification.objects.filter(
        recipient=request.user, is_read=False
    ).order_by("-created_at")
    count = unread_qs.count()
    # 알림 목록 페이지에서는 목록과 겹치므로 토스트 생략
    rm = getattr(request, "resolver_match", None)
    on_notif_list = rm and rm.url_name == "notification_list"
    toasts = (
        []
        if on_notif_list
        else list(unread_qs[:BOARD_NOTIFICATION_TOAST_LIMIT])
    )
    return {
        "unread_board_notification_count": count,
        "unread_board_notification_toasts": toasts,
    }


def visitor_stats(request):
    """
    모든 템플릿에서 접속자 통계를 사용할 수 있도록 context에 추가
    """
    return {
        'today_visitors': get_today_unique_visitors_count(),
        'total_visitors': get_total_visitors_count(),
    }

