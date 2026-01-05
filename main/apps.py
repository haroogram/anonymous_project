from django.apps import AppConfig
from django.core.management import call_command
from django.db import OperationalError


class MainConfig(AppConfig):
    name = 'main'
    _initial_data_loaded = False
    
    def ready(self):
        """앱이 준비되면 signals를 import하고 초기 데이터를 로드"""
        import main.signals  # noqa
        
        # 초기 데이터 자동 로드 (한 번만 실행)
        if not MainConfig._initial_data_loaded:
            self._load_initial_data()
            MainConfig._initial_data_loaded = True
    
    def _load_initial_data(self):
        """데이터베이스에 초기 데이터가 없으면 자동으로 로드"""
        try:
            from main.models import Category, Topic
            
            # 데이터베이스 테이블이 존재하는지 확인
            # Category 테이블이 없거나 데이터가 없으면 초기 데이터 로드
            category_count = Category.objects.count()
            
            if category_count == 0:
                # 초기 데이터 로드 실행
                try:
                    call_command('load_initial_data', verbosity=0)
                    print("✓ 초기 데이터가 자동으로 로드되었습니다.")
                except Exception as e:
                    # 커맨드 실행 실패 시 에러 로그만 출력 (앱 시작은 계속 진행)
                    print(f"⚠ 초기 데이터 로드 실패: {e}")
                    
        except OperationalError:
            # 데이터베이스 테이블이 아직 생성되지 않은 경우 (마이그레이션 전)
            # 이 경우는 무시하고 계속 진행
            pass
        except Exception as e:
            # 기타 예외는 무시 (앱 시작은 계속 진행)
            pass