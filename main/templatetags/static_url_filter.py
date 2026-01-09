"""
HTML 콘텐츠 내부의 static 경로를 STATIC_URL로 변환하는 템플릿 필터

S3를 사용하는 경우에도 HTML 콘텐츠 내부의 하드코딩된 /static/ 경로를
자동으로 올바른 STATIC_URL로 변환합니다.
"""
import re
from django import template
from django.conf import settings

register = template.Library()


@register.filter
def static_url(value):
    """
    HTML 콘텐츠 내부의 /static/ 경로를 STATIC_URL로 변환합니다.
    
    사용 예:
        {{ content|static_url|safe }}
    
    변환 예:
        /static/img/image.png -> https://bucket.s3.region.amazonaws.com/static/img/image.png
        또는 (로컬인 경우) -> /static/img/image.png
    """
    if not value:
        return value
    
    # STATIC_URL 가져오기
    static_url = settings.STATIC_URL
    
    # HTML 내부의 /static/ 경로를 찾아서 STATIC_URL로 변환
    # src="/static/...", href="/static/..." 등의 패턴 매칭
    pattern = r'(src|href)=["\'](/static/[^"\']+)["\']'
    
    def replace_static(match):
        attr = match.group(1)  # src 또는 href
        path = match.group(2)  # /static/... 경로 (예: /static/img/image.png)
        
        # STATIC_URL이 이미 전체 URL인 경우 (S3)와 상대 경로인 경우 모두 처리
        if static_url.startswith('http'):
            # S3 URL인 경우: STATIC_URL이 이미 /static/으로 끝나므로
            # /static/img/image.png -> img/image.png만 추출하여 STATIC_URL 뒤에 붙임
            relative_path = path[8:]  # /static/ 제거 (7글자)
            # STATIC_URL 끝에 슬래시가 있으면 그대로, 없으면 추가
            base_url = static_url.rstrip('/')
            new_url = f"{base_url}/{relative_path}"
        else:
            # 로컬 경로인 경우: STATIC_URL이 /static/이므로 그대로 사용
            # (이미 /static/으로 시작하는 경로이므로)
            new_url = path
        
        return f'{attr}="{new_url}"'
    
    # 패턴 매칭 및 치환
    result = re.sub(pattern, replace_static, str(value))
    
    return result

