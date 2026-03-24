from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


ERROR_META = {
    400: {
        "title": "잘못된 요청입니다.",
        "description": "요청 형식 또는 업로드 데이터가 올바르지 않습니다.",
    },
    403: {
        "title": "접근이 제한되었습니다.",
        "description": "권한이 없거나 보안 정책에 의해 요청이 거부되었습니다.",
    },
    404: {
        "title": "페이지를 찾을 수 없습니다.",
        "description": "주소가 변경되었거나 존재하지 않는 페이지입니다.",
    },
    413: {
        "title": "업로드 용량이 제한을 초과했습니다.",
        "description": "첨부 용량을 줄이거나 파일 개수를 나눠서 다시 시도해 주세요.",
    },
    500: {
        "title": "일시적인 서버 오류가 발생했습니다.",
        "description": "잠시 후 다시 시도해 주세요.",
    },
}


def _render_error(request: HttpRequest, status_code: int) -> HttpResponse:
    meta = ERROR_META.get(status_code, ERROR_META[500])
    context = {
        "status_code": status_code,
        "title": meta["title"],
        "description": meta["description"],
    }
    return render(request, "errors/common_error.html", context=context, status=status_code)


def bad_request(request: HttpRequest, exception) -> HttpResponse:
    return _render_error(request, 400)


def permission_denied(request: HttpRequest, exception) -> HttpResponse:
    return _render_error(request, 403)


def page_not_found(request: HttpRequest, exception) -> HttpResponse:
    return _render_error(request, 404)


def server_error(request: HttpRequest) -> HttpResponse:
    return _render_error(request, 500)


def csrf_failure(request: HttpRequest, reason: str = "") -> HttpResponse:
    return _render_error(request, 403)


def error_page(request: HttpRequest, status_code: int) -> HttpResponse:
    # CloudFront Custom Error Response에서 단순 GET 라우팅용
    if status_code not in ERROR_META:
        status_code = 500
    return _render_error(request, status_code)
