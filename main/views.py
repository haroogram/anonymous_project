from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.db.models import Q
from django.views.decorators.cache import cache_page
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.core.mail import send_mail

from .models import Category, Topic
from .utils import (
    get_visitor_stats,
    get_today_visitors_count,
    get_total_visitors_count,
    get_daily_visitors_count,
)
from .forms import SignupForm, LoginForm
from .tokens import account_activation_token


def cache_page_by_auth(timeout):
    """
    로그인 여부(익명/로그인)에 따라 캐시 키 prefix를 다르게 주는 데코레이터.
    익명 유저: key_prefix='anon'
    로그인 유저: key_prefix='auth'
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            key_prefix = 'auth' if request.user.is_authenticated else 'anon'
            cached_view = cache_page(timeout, key_prefix=key_prefix)(view_func)
            return cached_view(request, *args, **kwargs)
        return _wrapped_view
    return decorator


# 개발 환경에서는 캐싱 비활성화, 프로덕션에서는 24시간 캐싱
cache_timeout = 0 if settings.DEBUG else 60 * 60 * 24


@cache_page_by_auth(cache_timeout)
def index(request):
    """메인 페이지"""
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'main/index.html', context)


@cache_page_by_auth(cache_timeout)
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


@cache_page_by_auth(cache_timeout)
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


def healthz(request):
    """
    Health check 엔드포인트
    ASG/Target Group health check용
    """
    return JsonResponse({'status': 'ok'}, status=200)


@cache_page_by_auth(cache_timeout)
def about(request):
    """프로젝트 소개 페이지"""
    return render(request, 'main/about.html')


def signup(request):
    """회원가입"""
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user: User = form.save(commit=False)
            # 이메일 인증 전까지 비활성화
            user.is_active = False
            user.email = form.cleaned_data.get('email')
            user.save()

            # 이메일 인증 링크 발송
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            activate_url = request.build_absolute_uri(
                reverse('auth_activate', kwargs={'uidb64': uid, 'token': token})
            )

            subject = 'Anonymous Project 계정 활성화 안내'
            message = (
                f'안녕하세요, Anonymous Project 입니다.\n\n'
                f'다음 링크를 클릭하여 계정을 활성화해 주세요:\n\n'
                f'{activate_url}\n\n'
                f'이 링크는 일정 시간 후 만료될 수 있습니다.\n\n'
                f'감사합니다.'
            )

            send_mail(
                subject,
                message,
                None,
                [user.email],
                fail_silently=False,
            )
            return redirect('auth_signup_complete')
    else:
        form = SignupForm()

    return render(request, 'auth/signup.html', {'form': form})


def login_view(request):
    """로그인"""
    if request.user.is_authenticated:
        return redirect('index')

    next_url = request.GET.get('next') or request.POST.get('next')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_active:
                messages.error(request, '이메일 인증이 완료되지 않은 계정입니다.')
            else:
                login(request, user)
                redirect_to = next_url or reverse('index')
                return HttpResponseRedirect(redirect_to)
    else:
        form = LoginForm()

    context = {
        'form': form,
        'next': next_url,
    }
    return render(request, 'auth/login.html', context)


def logout_view(request):
    """로그아웃"""
    if request.method == 'POST' or request.GET.get('next') is not None:
        logout(request)
        next_url = request.GET.get('next') or reverse('index')
        return HttpResponseRedirect(next_url)

    # GET 요청에서 단순 확인 후 로그아웃 처리
    logout(request)
    return redirect('index')


def activate(request, uidb64, token):
    """
    이메일 인증 링크 처리
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if not user.is_active:
            user.is_active = True
            user.save()
            messages.success(
                request,
                '회원가입과 이메일 인증이 모두 완료되었습니다. 이제 Anonymous Project에 로그인하여 튜토리얼을 이용하실 수 있습니다.',
            )
        else:
            messages.info(request, '이미 활성화된 계정입니다. 바로 로그인할 수 있습니다.')
        return redirect('auth_login')

    messages.error(request, '유효하지 않거나 만료된 인증 링크입니다.')
    return render(request, 'auth/activation_invalid.html')


def signup_complete(request):
    """회원가입 완료 안내 페이지"""
    return render(request, 'auth/signup_complete.html')