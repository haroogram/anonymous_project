"""
접속자 수 추적을 위한 Redis 유틸리티 함수들
"""
from datetime import datetime, date
from django.conf import settings
from django.db import models
from django_redis import get_redis_connection
import logging

logger = logging.getLogger(__name__)

# Redis 키 패턴
TODAY_VISITORS_KEY = 'visitors:today'  # 오늘 접속자 수
TOTAL_VISITORS_KEY = 'visitors:total'  # 누적 접속자 수
DAILY_VISITORS_KEY_PREFIX = 'visitors:daily:'  # 일별 접속자 수 (예: visitors:daily:2024-01-01)
VISITOR_SET_KEY_PREFIX = 'visitors:set:'  # 일별 접속자 집합 (중복 제거용)


def get_redis_client():
    """
    Redis 클라이언트 연결 반환
    """
    try:
        return get_redis_connection('default')
    except Exception as e:
        logger.error(f"Redis 연결 실패: {e}")
        return None


def get_today_date_str():
    """
    오늘 날짜를 YYYY-MM-DD 형식 문자열로 반환
    """
    return date.today().strftime('%Y-%m-%d')


def increment_visitor_count(ip_address=None, user_agent=None):
    """
    접속자 수를 증가시킵니다.
    
    Args:
        ip_address: 접속자의 IP 주소 (중복 제거용)
        user_agent: 접속자의 User-Agent (선택사항)
    
    Returns:
        tuple: (오늘 접속자 수, 누적 접속자 수) 또는 None (Redis 연결 실패 시)
    """
    redis_client = get_redis_client()
    if not redis_client:
        return None
    
    try:
        today = get_today_date_str()
        daily_key = f"{DAILY_VISITORS_KEY_PREFIX}{today}"
        visitor_set_key = f"{VISITOR_SET_KEY_PREFIX}{today}"
        
        pipe = redis_client.pipeline()
        
        # 오늘 날짜 키에 1 증가 (일별 접속자 수)
        pipe.incr(daily_key)
        pipe.expire(daily_key, 60 * 60 * 24 * 30)  # 30일 후 만료
        
        # 누적 접속자 수 증가
        pipe.incr(TOTAL_VISITORS_KEY)
        
        # IP 주소를 세트에 추가하여 중복 접속자 제거 (같은 IP는 하루에 한 번만 카운트)
        if ip_address:
            pipe.sadd(visitor_set_key, ip_address)
            pipe.expire(visitor_set_key, 60 * 60 * 24 * 30)  # 30일 후 만료
        
        results = pipe.execute()
        
        today_count = results[0]  # daily_key의 증가된 값
        total_count = results[1]  # TOTAL_VISITORS_KEY의 증가된 값
        
        return today_count, total_count
        
    except Exception as e:
        logger.error(f"접속자 수 증가 실패: {e}")
        return None


def get_today_visitors_count():
    """
    오늘 접속자 수를 반환합니다.
    
    Returns:
        int: 오늘 접속자 수, Redis 연결 실패 시 0
    """
    redis_client = get_redis_client()
    if not redis_client:
        return 0
    
    try:
        today = get_today_date_str()
        daily_key = f"{DAILY_VISITORS_KEY_PREFIX}{today}"
        count = redis_client.get(daily_key)
        return int(count) if count else 0
    except Exception as e:
        logger.error(f"오늘 접속자 수 조회 실패: {e}")
        return 0


def get_today_unique_visitors_count():
    """
    오늘 고유 접속자 수를 반환합니다 (IP 기반 중복 제거).
    
    Returns:
        int: 오늘 고유 접속자 수, Redis 연결 실패 시 0
    """
    redis_client = get_redis_client()
    if not redis_client:
        return 0
    
    try:
        today = get_today_date_str()
        visitor_set_key = f"{VISITOR_SET_KEY_PREFIX}{today}"
        count = redis_client.scard(visitor_set_key)
        return count if count else 0
    except Exception as e:
        logger.error(f"오늘 고유 접속자 수 조회 실패: {e}")
        return 0


def get_total_visitors_count():
    """
    누적 접속자 수를 반환합니다 (DB에 저장된 일별 unique_visitor_count의 총합).
    오늘 날짜의 데이터는 아직 DB에 동기화되지 않았을 수 있으므로 Redis에서 가져와 합산합니다.
    
    Returns:
        int: 누적 접속자 수 (DB의 unique_visitor_count 합계 + 오늘의 unique_visitor_count)
    """
    from main.models import VisitorStats
    
    try:
        today = date.today()
        
        # DB에 저장된 모든 날짜의 unique_visitor_count 합계
        db_total = VisitorStats.objects.aggregate(
            total=models.Sum('unique_visitor_count')
        )['total'] or 0
        
        # 오늘 날짜가 DB에 있는지 확인
        today_stats = VisitorStats.objects.filter(date=today).first()
        
        if today_stats:
            # 오늘 날짜가 DB에 있으면 DB 값을 사용 (이미 합계에 포함되어 있음)
            return int(db_total)
        else:
            # 오늘 날짜가 DB에 없으면 Redis에서 오늘의 unique_visitor_count를 가져와 합산
            today_unique = get_today_unique_visitors_count()
            return int(db_total) + int(today_unique)
            
    except Exception as e:
        logger.error(f"누적 접속자 수 조회 실패: {e}")
        return 0


def get_daily_visitors_count(target_date=None):
    """
    특정 날짜의 접속자 수를 반환합니다.
    
    Args:
        target_date: 날짜 객체 또는 YYYY-MM-DD 형식 문자열. None이면 오늘 날짜 사용.
    
    Returns:
        int: 해당 날짜의 접속자 수
    """
    redis_client = get_redis_client()
    if not redis_client:
        return 0
    
    try:
        if target_date is None:
            date_str = get_today_date_str()
        elif isinstance(target_date, date):
            date_str = target_date.strftime('%Y-%m-%d')
        else:
            date_str = str(target_date)
        
        daily_key = f"{DAILY_VISITORS_KEY_PREFIX}{date_str}"
        count = redis_client.get(daily_key)
        return int(count) if count else 0
    except Exception as e:
        logger.error(f"일별 접속자 수 조회 실패: {e}")
        return 0


def get_visitor_stats():
    """
    접속자 통계를 딕셔너리로 반환합니다.
    
    Returns:
        dict: {
            'today': 오늘 접속자 수,
            'today_unique': 오늘 고유 접속자 수,
            'total': 누적 접속자 수,
            'date': 오늘 날짜 (YYYY-MM-DD)
        }
    """
    return {
        'today': get_today_visitors_count(),
        'today_unique': get_today_unique_visitors_count(),
        'total': get_total_visitors_count(),
        'date': get_today_date_str(),
    }


def get_daily_unique_visitors_count(target_date=None):
    """특정 날짜의 고유 접속자 수를 반환"""
    redis_client = get_redis_client()
    if not redis_client:
        return 0
    
    try:
        if target_date is None:
            date_str = get_today_date_str()
        elif isinstance(target_date, date):
            date_str = target_date.strftime('%Y-%m-%d')
        else:
            date_str = str(target_date)
        
        visitor_set_key = f"{VISITOR_SET_KEY_PREFIX}{date_str}"
        count = redis_client.scard(visitor_set_key)
        return count if count else 0
    except Exception as e:
        logger.error(f"일별 고유 접속자 수 조회 실패: {e}")
        return 0


def get_visitor_count_from_db(target_date):
    """
    MariaDB에서 접속자 수 조회 (Redis에 없을 때 사용)
    
    Args:
        target_date: date 객체 또는 YYYY-MM-DD 문자열
    
    Returns:
        dict: {'visitor_count': int, 'unique_visitor_count': int} 또는 None
    """
    from main.models import VisitorStats
    
    try:
        if isinstance(target_date, str):
            target_date = date.fromisoformat(target_date)
        
        stats = VisitorStats.objects.get(date=target_date)
        return {
            'visitor_count': stats.visitor_count,
            'unique_visitor_count': stats.unique_visitor_count,
        }
    except VisitorStats.DoesNotExist:
        return None
    except Exception as e:
        logger.error(f"DB에서 접속자 수 조회 실패: {e}")
        return None