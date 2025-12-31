"""
Redis에서 MariaDB로 접속자 수 통계 동기화 커맨드
매일 자정에 실행 (cron): python manage.py sync_visitor_stats

사용법:
    # 전날 데이터 동기화
    python manage.py sync_visitor_stats
    
    # 특정 날짜 동기화
    python manage.py sync_visitor_stats --date 2024-01-14
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from main.models import VisitorStats
from main.utils import (
    get_daily_visitors_count,
    get_daily_unique_visitors_count,
    get_redis_client,
    DAILY_VISITORS_KEY_PREFIX,
    VISITOR_SET_KEY_PREFIX
)
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Redis의 접속자 수 통계를 MariaDB에 동기화합니다'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='동기화할 날짜 (YYYY-MM-DD 형식, 미지정 시 전날)',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='동기화할 일수 (기본값: 1, 전날만)',
        )

    def handle(self, *args, **options):
        target_date_str = options.get('date')
        days = options.get('days', 1)

        if target_date_str:
            try:
                target_date = date.fromisoformat(target_date_str)
            except ValueError:
                self.stdout.write(self.style.ERROR(f'잘못된 날짜 형식: {target_date_str}'))
                return
        else:
            # 전날 날짜
            target_date = date.today() - timedelta(days=1)

        self.stdout.write(f'{target_date} 데이터 동기화를 시작합니다...')

        sync_count = 0
        for i in range(days):
            sync_date = target_date - timedelta(days=i)
            if self.sync_date(sync_date):
                sync_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'성공적으로 {sync_count}일의 데이터를 동기화했습니다.')
        )

    def sync_date(self, target_date):
        """특정 날짜의 데이터를 동기화"""
        date_str = target_date.strftime('%Y-%m-%d')
        
        try:
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
            self.stdout.write(
                self.style.SUCCESS(
                    f'{date_str}: 접속자 {visitor_count}명, 고유 접속자 {unique_visitor_count}명 ({action})'
                )
            )
            return True

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'{date_str} 동기화 실패: {e}')
            )
            logger.error(f'{date_str} 동기화 실패: {e}', exc_info=True)
            return False