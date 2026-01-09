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
    
    # STATIC_URL 가져오기 (끝에 슬래시 보장)
    static_url = settings.STATIC_URL.rstrip('/') + '/'
    
    # HTML 내부의 /static/ 경로를 찾아서 STATIC_URL로 변환
    # src="/static/...", href="/static/..." 등의 패턴 매칭
    pattern = r'(src|href)=["\'](/static/[^"\']+)["\']'
    
    def replace_static(match):
        attr = match.group(1)  # src 또는 href
        path = match.group(2)  # /static/... 경로 (예: /static/img/image.png)
        
        # /static/을 STATIC_URL로 교체
        # 예: /static/img/image.png -> https://bucket.s3.region.amazonaws.com/static/img/image.png
        # 또는 (로컬): /static/img/image.png -> /static/img/image.png
        new_url = path.replace('/static/', static_url, 1)
        
        return f'{attr}="{new_url}"'
    
    # 패턴 매칭 및 치환
    result = re.sub(pattern, replace_static, str(value))
    
    return result

