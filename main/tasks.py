"""
Celery 비동기 작업 정의
"""
from celery import shared_task
import logging
from datetime import date, timedelta

logger = logging.getLogger(__name__)


@shared_task(bind=True, name='main.tasks.sync_visitor_stats_task')
def sync_visitor_stats_task(self):
    """
    매일 자정에 실행되는 배치 작업
    Redis의 전날 접속자 수 통계를 MariaDB에 동기화합니다.
    
    Returns:
        dict: 동기화 결과 정보
    """
    from main.models import VisitorStats
    from main.utils import get_daily_visitors_count, get_daily_unique_visitors_count
    
    try:
        # 전날 날짜
        target_date = date.today() - timedelta(days=1)
        date_str = target_date.strftime('%Y-%m-%d')
        
        logger.info(f'접속자 수 동기화 시작: {date_str}')
        
        # Redis에서 데이터 가져오기
        visitor_count = get_daily_visitors_count(target_date)
        unique_visitor_count = get_daily_unique_visitors_count(target_date)
        
        # MariaDB에 저장 또는 업데이트
        visitor_stats, created = VisitorStats.objects.update_or_create(
            date=target_date,
            defaults={
                'visitor_count': visitor_count,
                'unique_visitor_count': unique_visitor_count,
            }
        )
        
        action = '생성' if created else '업데이트'
        result_msg = (
            f'{date_str}: 접속자 {visitor_count}명, '
            f'고유 접속자 {unique_visitor_count}명 ({action})'
        )
        
        logger.info(f'접속자 수 동기화 완료: {result_msg}')
        
        return {
            'success': True,
            'date': date_str,
            'visitor_count': visitor_count,
            'unique_visitor_count': unique_visitor_count,
            'action': action,
            'message': result_msg,
        }
        
    except Exception as exc:
        error_msg = f'접속자 수 동기화 실패: {exc}'
        logger.error(error_msg, exc_info=True)
        
        # Celery의 retry 메커니즘 활용 (선택사항)
        # raise self.retry(exc=exc, countdown=60, max_retries=3)
        
        return {
            'success': False,
            'error': str(exc),
            'message': error_msg,
        }

