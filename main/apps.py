from django.apps import AppConfig


class MainConfig(AppConfig):
    name = 'main'
    
    def ready(self):
        """앱이 준비되면 signals를 import"""
        import main.signals  # noqa