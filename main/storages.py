"""
커스텀 Storage Backend 정의
S3에 static 파일을 저장하기 위한 커스텀 Storage 클래스
"""
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from django.contrib.staticfiles.storage import ManifestFilesMixin


class ManifestStaticStorage(ManifestFilesMixin, S3Boto3Storage):
    """
    ManifestStaticFilesStorage 기능을 지원하는 S3 Storage 클래스
    
    파일 내용의 해시를 파일명에 추가하여 캐시 무효화 문제를 해결합니다.
    예: style.css -> style.abc123def.css
    
    CSS/JS 파일이 변경되면 자동으로 새로운 URL이 생성되어
    브라우저가 새로운 파일을 다운로드합니다.
    
    CDN_DOMAIN이 설정되어 있으면 CDN URL로 반환합니다.
    """
    location = "static"
    default_acl = None
    file_overwrite = False  # 같은 이름의 파일 덮어쓰기 방지
    querystring_auth = False  # URL에 인증 정보 포함하지 않음
    
    # S3 객체 파라미터
    object_parameters = {
        'CacheControl': 'max-age=31536000',  # 1년 캐시 (파일명에 해시가 있으므로 안전)
    }
    
    def url(self, name, parameters=None, expire=None, http_method=None):
        """
        CDN 도메인이 설정되어 있으면 CDN URL 반환, 아니면 S3 URL 반환
        """
        cdn_domain = getattr(settings, 'CDN_DOMAIN', None)
        if cdn_domain:
            # CDN 도메인을 통한 URL 생성
            return f"https://{cdn_domain}/{self.location}/{name}"
        # CDN 미설정 시 기본 S3 URL 사용
        return super().url(name, parameters=parameters, expire=expire, http_method=http_method)


class StaticStorage(S3Boto3Storage):
    """
    Static files를 S3에 저장하기 위한 커스텀 Storage 클래스
    
    location = "static"을 설정하여 S3 버킷 내에서 
    static 파일들이 "static/" 경로 하위에 저장되도록 합니다.
    
    Note: Manifest 기능 없이 사용하려면 이 클래스를 사용하세요.
    """
    location = "static"
    default_acl = None
    file_overwrite = False  # 같은 이름의 파일 덮어쓰기 방지
    querystring_auth = False  # URL에 인증 정보 포함하지 않음
    
    # S3 객체 파라미터
    object_parameters = {
        'CacheControl': 'max-age=86400',  # 1일 캐시
    }
