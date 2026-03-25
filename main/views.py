from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse, JsonResponse, HttpResponseRedirect
from django.db import transaction
from django.db.models import Count, Q
from django.core.exceptions import ValidationError
from django.core.cache import cache
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
import logging
import hashlib
import uuid

from .models import BoardAttachment, BoardPost, Category, Topic
from .board_attachments import validate_board_uploaded_files
from .board_password import upgrade_stored_password_if_legacy, verify_board_password
from .utils import (
    get_visitor_stats,
    get_today_visitors_count,
    get_total_visitors_count,
    get_daily_visitors_count,
    get_client_ip,
)
from .forms import SignupForm, LoginForm, BoardPostForm
from .tokens import account_activation_token

logger = logging.getLogger(__name__)
rate_limit_logger = logging.getLogger("security.ratelimit")


def _board_rate_limit_exceeded(request, action: str) -> bool:
    """
    비회원 게시판 POST 요청에 대한 간단한 캐시 기반 rate limit.
    키는 (action + client_ip + anonymous_id 쿠키) 단위로 관리합니다.
    """
    limit = int(getattr(settings, "BOARD_POST_RATE_LIMIT_COUNT", 20))
    window = int(getattr(settings, "BOARD_POST_RATE_LIMIT_WINDOW_SEC", 300))
    if limit <= 0 or window <= 0:
        return False

    client_ip = get_client_ip(request)
    anon_id = request.COOKIES.get("ap_anon_id", "no-anon-id")
    cache_key = f"ratelimit:board:{action}:{client_ip}:{anon_id}"

    current = cache.get(cache_key)
    if current is None:
        cache.set(cache_key, 1, timeout=window)
        return False

    try:
        current = cache.incr(cache_key)
    except Exception:
        # 일부 캐시 백엔드는 incr 지원이 제한될 수 있어 set fallback 사용
        current = int(current) + 1
        cache.set(cache_key, current, timeout=window)
    return int(current) > limit


def _wants_json_response(request) -> bool:
    if request.path.startswith("/api/"):
        return True
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return True
    accept = (request.headers.get("Accept") or "").lower()
    return "application/json" in accept and "text/html" not in accept


def _rate_limit_response(request, action: str):
    retry_after = int(getattr(settings, "BOARD_POST_RATE_LIMIT_WINDOW_SEC", 300))
    client_ip = get_client_ip(request)
    anon_id = request.COOKIES.get("ap_anon_id", "")
    anon_id_hash = hashlib.sha256(anon_id.encode("utf-8")).hexdigest()[:12] if anon_id else "-"

    rate_limit_logger.warning(
        "event=rate_limit_block scope=board_post action=%s method=%s path=%s ip=%s anon_id_hash=%s ua=%s retry_after=%s",
        action,
        request.method,
        request.path,
        client_ip,
        anon_id_hash,
        request.META.get("HTTP_USER_AGENT", ""),
        retry_after,
    )
    payload = {
        "error": "rate_limited",
        "message": "요청이 너무 많습니다. 잠시 후 다시 시도해 주세요.",
        "action": action,
        "retry_after": retry_after,
    }

    if _wants_json_response(request):
        response = JsonResponse(payload, status=429, json_dumps_params={"ensure_ascii": False})
    else:
        response = render(
            request,
            "errors/common_error.html",
            {
                "status_code": 429,
                "title": "요청이 너무 많습니다.",
                "description": f"잠시 후 다시 시도해 주세요. (약 {retry_after}초 후 재시도 권장)",
            },
            status=429,
        )
    response["Retry-After"] = str(retry_after)
    return response


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
                f'이 링크는 발송 시점부터 1시간 후 만료됩니다.\n\n'
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


def board_list(request):
    """자유게시판 목록"""
    posts = (
        BoardPost.objects.filter(is_deleted=False)
        .annotate(attachment_count=Count("attachments", distinct=True))
        .order_by("-created_at")
    )
    context = {
        "posts": posts,
    }
    return render(request, "board/board_list.html", context)


def board_detail(request, pk):
    """자유게시판 상세"""
    post = get_object_or_404(
        BoardPost.objects.prefetch_related("attachments"),
        pk=pk,
        is_deleted=False,
    )
    context = {
        "post": post,
    }
    return render(request, "board/board_detail.html", context)


def board_attachment_download(request, post_pk, attachment_pk):
    """첨부파일 다운로드 (게시글이 삭제되지 않은 경우만)."""
    post = get_object_or_404(BoardPost, pk=post_pk, is_deleted=False)
    attachment = get_object_or_404(BoardAttachment, pk=attachment_pk, post=post)
    filename = attachment.original_name or attachment.file.name.rsplit("/", 1)[-1]
    file_handle = attachment.file.open("rb")
    return FileResponse(
        file_handle,
        as_attachment=True,
        filename=filename,
    )


def _make_masked_author_from_ip(ip: str) -> str:
    """
    IP 기반 익명 작성자명 생성.
    예: 112.221.33.44 -> 익명(112.221.xxx.xxx)
    """
    if not ip:
        return "익명(anonymous)"

    # IPv4 형식 우선 처리
    parts = ip.split(".")
    if len(parts) == 4 and all(part.isdigit() for part in parts):
        return f"익명({parts[0]}.{parts[1]}.xxx.xxx)"

    # 그 외(IPV6 등)는 앞부분만 간단히 마스킹
    return f"익명({ip[:6]}**)"


def _board_form_context():
    return {
        "board_allowed_extensions": sorted(
            getattr(settings, "BOARD_ATTACHMENT_ALLOWED_EXTENSIONS", ())
        ),
        "board_max_attachments": getattr(settings, "BOARD_ATTACHMENT_MAX_COUNT", 5),
        "board_max_file_mb": getattr(
            settings, "BOARD_ATTACHMENT_MAX_BYTES", 10 * 1024 * 1024
        )
        // (1024 * 1024),
    }


def _verified_remove_attachment_ids(post, request):
    """POST의 remove_attachments가 해당 글의 첨부만 포함하는지 검증. 실패 시 None."""
    raw = request.POST.getlist("remove_attachments")
    if not raw:
        return set()
    ids = [int(x) for x in raw if str(x).isdigit()]
    if not ids:
        return set()
    found = set(post.attachments.filter(pk__in=ids).values_list("pk", flat=True))
    if set(ids) != found:
        return None
    return found


def _save_new_attachments(post, files):
    for f in files:
        BoardAttachment.objects.create(
            post=post,
            file=f,
            original_name=getattr(f, "name", "") or "",
            size=getattr(f, "size", 0) or 0,
        )


def _get_or_create_anonymous_id(request):
    """
    쿠키 기반 익명 ID 조회/생성.
    Returns:
        tuple[str, bool]: (anonymous_id, is_new)
    """
    anon_id = request.COOKIES.get("ap_anon_id")
    is_new = False
    if not anon_id:
        anon_id = uuid.uuid4().hex
        is_new = True
    return anon_id, is_new


def board_create(request):
    """자유게시판 글 작성 (비로그인)"""
    if request.method == "POST":
        if _board_rate_limit_exceeded(request, "create"):
            return _rate_limit_response(request, "create")
        form = BoardPostForm(request.POST)
        files = request.FILES.getlist("attachments")
        if form.is_valid():
            try:
                validate_board_uploaded_files(files, current_count=0)
            except ValidationError as e:
                for msg in e.messages:
                    form.add_error(None, msg)
            else:
                with transaction.atomic():
                    post = form.save(commit=False)
                    client_ip = get_client_ip(request)
                    post.author_name = _make_masked_author_from_ip(client_ip)
                    anon_id, is_new = _get_or_create_anonymous_id(request)
                    post.anonymous_id = anon_id
                    post.save()
                    _save_new_attachments(post, files)
                messages.success(request, "게시글이 등록되었습니다.")
                response = redirect("board_list")
                if is_new:
                    response.set_cookie(
                        "ap_anon_id",
                        anon_id,
                        max_age=60 * 60 * 24 * 365,  # 1년
                        httponly=True,
                        samesite="Lax",
                    )
                return response
    else:
        form = BoardPostForm()

    ctx = {"form": form, **_board_form_context()}
    return render(request, "board/board_form.html", ctx)


def board_update(request, pk):
    """자유게시판 글 수정 (비밀번호 확인)"""
    post = get_object_or_404(
        BoardPost.objects.prefetch_related("attachments"),
        pk=pk,
        is_deleted=False,
    )

    if request.method == "POST":
        if _board_rate_limit_exceeded(request, "update"):
            return _rate_limit_response(request, "update")
        form = BoardPostForm(request.POST, instance=post)
        input_password = request.POST.get("password", "")
        files = request.FILES.getlist("attachments")
        remove_ids = _verified_remove_attachment_ids(post, request)

        if remove_ids is None:
            messages.error(request, "삭제할 첨부 정보가 올바르지 않습니다.")
        elif form.is_valid():
            if not verify_board_password(input_password, post.password):
                form.add_error("password", "비밀번호가 일치하지 않습니다.")
            else:
                remaining = post.attachments.exclude(pk__in=remove_ids or set()).count()
                try:
                    validate_board_uploaded_files(files, current_count=remaining)
                except ValidationError as e:
                    for msg in e.messages:
                        form.add_error(None, msg)
                else:
                    with transaction.atomic():
                        form.save()
                        if remove_ids:
                            for att in post.attachments.filter(pk__in=remove_ids):
                                att.delete()
                        _save_new_attachments(post, files)
                    messages.success(request, "게시글이 수정되었습니다.")
                    return redirect("board_detail", pk=post.pk)
    else:
        # 비밀번호는 다시 입력받기 위해 초기값 제거
        initial_data = {
            "title": post.title,
            "content": post.content,
        }
        form = BoardPostForm(initial=initial_data)

    ctx = {"form": form, "post": post, **_board_form_context()}
    return render(request, "board/board_form.html", ctx)


def board_delete(request, pk):
    """자유게시판 글 삭제 (비밀번호 확인, soft delete)"""
    post = get_object_or_404(BoardPost, pk=pk, is_deleted=False)

    if request.method == "POST":
        if _board_rate_limit_exceeded(request, "delete"):
            return _rate_limit_response(request, "delete")
        input_password = request.POST.get("password", "")
        if not verify_board_password(input_password, post.password):
            messages.error(request, "비밀번호가 일치하지 않습니다.")
            return redirect("board_detail", pk=post.pk)

        upgrade_stored_password_if_legacy(post, input_password)
        post.is_deleted = True
        post.save(update_fields=["is_deleted"])
        messages.success(request, "게시글이 삭제되었습니다.")
        return redirect("board_list")

    return render(request, "board/board_confirm_delete.html", {"post": post})