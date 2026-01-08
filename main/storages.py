"""
커스텀 Storage Backend 정의
S3에 static 파일을 저장하기 위한 커스텀 Storage 클래스
"""
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    """
    Static files를 S3에 저장하기 위한 커스텀 Storage 클래스
    
    location = "static"을 설정하여 S3 버킷 내에서 
    static 파일들이 "static/" 경로 하위에 저장되도록 합니다.
    """
    location = "static"
    default_acl = "public-read"
    file_overwrite = False  # 같은 이름의 파일 덮어쓰기 방지
    querystring_auth = False  # URL에 인증 정보 포함하지 않음
    
    # S3 객체 파라미터
    object_parameters = {
        'CacheControl': 'max-age=86400',  # 1일 캐시
    }
