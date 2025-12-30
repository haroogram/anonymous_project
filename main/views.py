from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.cache import cache_page
from .models import Category, Topic
from .utils import get_visitor_stats, get_today_visitors_count, get_total_visitors_count, get_daily_visitors_count


@cache_page(60 * 60 * 24)  # 24시간 캐싱
def index(request):
    """메인 페이지"""
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'main/index.html', context)


@cache_page(60 * 60 * 24)  # 24시간 캐싱
def tutorial(request, category):
    """카테고리별 튜토리얼 목록"""
    category_obj = get_object_or_404(Category, slug=category)
    topics = Topic.objects.filter(category=category_obj)
    
    context = {
        'category': category,
        'category_obj': category_obj,
        'category_name': category_obj.name,
        'topics': topics,
    }
    return render(request, 'main/tutorial.html', context)


@cache_page(60 * 60 * 24)  # 24시간 캐싱
def topic_detail(request, category, topic):
    """주제 상세 페이지"""
    category_obj = get_object_or_404(Category, slug=category)
    topic_obj = get_object_or_404(Topic, category=category_obj, slug=topic)
    
    # 같은 카테고리의 다른 주제들 가져오기 (사이드바용)
    topics = Topic.objects.filter(category=category_obj)
    
    context = {
        'category': category,
        'category_obj': category_obj,
        'category_name': category_obj.name,
        'topic': topic,  # sidebar의 active 클래스 비교를 위해 slug 문자열 유지
        'topic_obj': topic_obj,
        'title': topic_obj.title,
        'content': topic_obj.content,
        'topics': topics,
    }
    return render(request, 'main/topic_detail.html', context)


def visitor_stats(request):
    """
    접속자 수 통계 API
    
    Returns:
        JSON: {
            'today': 오늘 접속자 수,
            'today_unique': 오늘 고유 접속자 수,
            'total': 누적 접속자 수,
            'date': 오늘 날짜 (YYYY-MM-DD)
        }
    """
    stats = get_visitor_stats()
    return JsonResponse(stats)


def visitor_stats_detail(request):
    """접속자 수 상세 통계 API"""
    target_date = request.GET.get('date')
    
    if target_date:
        # 과거 날짜는 DB에서 조회
        from main.utils import get_visitor_count_from_db
        from datetime import date as date_class
        
        try:
            query_date = date_class.fromisoformat(target_date)
            today = date_class.today()
            
            # 오늘 이전 날짜는 DB에서 조회
            if query_date < today:
                db_stats = get_visitor_count_from_db(query_date)
                if db_stats:
                    return JsonResponse({
                        'date': target_date,
                        'today': db_stats['visitor_count'],
                        'today_unique': db_stats['unique_visitor_count'],
                        'total': get_total_visitors_count(),
                    })
        except ValueError:
            pass
        
        # 오늘 날짜이거나 DB에 없는 경우 Redis에서 조회
        daily_count = get_daily_visitors_count(target_date)
        return JsonResponse({
            'date': target_date,
            'today': daily_count,
            'total': get_total_visitors_count(),
        })
    else:
        # 오늘은 Redis에서 조회
        return JsonResponse({
            'today': get_today_visitors_count(),
            'total': get_total_visitors_count(),
            'date': get_visitor_stats()['date'],
        })


def search(request):
    """검색 기능"""
    query = request.GET.get('q', '').strip()
    results = []
    
    if query:
        # 제목과 내용에서 검색 (대소문자 구분 없음)
        topics = Topic.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).select_related('category').order_by('category__order', 'order')
        
        # 검색 결과를 카테고리별로 그룹화
        results_by_category = {}
        for topic in topics:
            category_name = topic.category.name
            if category_name not in results_by_category:
                results_by_category[category_name] = {
                    'category': topic.category,
                    'topics': []
                }
            results_by_category[category_name]['topics'].append(topic)
        
        results = list(results_by_category.values())
    
    context = {
        'query': query,
        'results': results,
        'results_count': sum(len(r['topics']) for r in results) if results else 0,
    }
    return render(request, 'main/search.html', context)
