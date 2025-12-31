"""
Django signals for cache invalidation
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Category, Topic


@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
def invalidate_category_cache(sender, instance, **kwargs):
    """Category가 변경되면 관련 캐시 무효화"""
    # 메인 페이지 캐시 무효화
    cache.delete('index_categories')
    
    # 해당 카테고리의 튜토리얼 목록 캐시 무효화
    cache_key_pattern = f'tutorial_{instance.slug}'
    # cache_page는 URL 기반으로 키를 생성하므로 정확한 키를 알기 어려움
    # 대신 cache.clear()를 사용하거나, 더 세밀한 제어가 필요하면 수동 캐싱으로 변경


@receiver(post_save, sender=Topic)
@receiver(post_delete, sender=Topic)
def invalidate_topic_cache(sender, instance, **kwargs):
    """Topic이 변경되면 관련 캐시 무효화"""
    # 해당 주제의 상세 페이지 캐시 무효화
    cache_key_pattern = f'topic_detail_{instance.category.slug}_{instance.slug}'
    
    # 해당 카테고리의 튜토리얼 목록 캐시 무효화
    tutorial_cache_key_pattern = f'tutorial_{instance.category.slug}'
    
    # 메인 페이지 캐시 무효화
    cache.delete('index_categories')
    
    # cache_page는 내부적으로 복잡한 키를 사용하므로
    # 전체 캐시를 클리어하거나, 더 세밀한 제어를 위해
    # django.core.cache.cache.clear()를 사용할 수 있지만
    # 이는 모든 캐시를 지우므로 주의가 필요함
    
    # 대안: 특정 패턴의 키만 삭제하려면 Redis를 직접 사용
    # 또는 cache_page 대신 수동 캐싱을 사용하는 것이 더 나을 수 있음

