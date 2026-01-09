"""
초기 데이터 로드 커맨드
사용법: python manage.py load_initial_data
"""
from django.core.management.base import BaseCommand
from main.models import Category, Topic
from main.management.commands import initial_topics_data


class Command(BaseCommand):
    help = '초기 카테고리 및 주제 데이터를 데이터베이스에 로드합니다'

    def handle(self, *args, **options):
        self.stdout.write('초기 데이터 로드를 시작합니다...')
        
        # 기존 데이터베이스 초기화
        self.stdout.write('\n기존 데이터를 초기화합니다...')
        try:
            topic_count = Topic.objects.count()
            category_count = Category.objects.count()
            
            if topic_count > 0:
                self.stdout.write(f'  {topic_count}개의 주제를 삭제합니다...')
                Topic.objects.all().delete()
                self.stdout.write(self.style.SUCCESS(f'  {topic_count}개의 주제가 삭제되었습니다.'))
            else:
                self.stdout.write(self.style.WARNING('  삭제할 주제가 없습니다.'))
            
            if category_count > 0:
                self.stdout.write(f'  {category_count}개의 카테고리를 삭제합니다...')
                Category.objects.all().delete()
                self.stdout.write(self.style.SUCCESS(f'  {category_count}개의 카테고리가 삭제되었습니다.'))
            else:
                self.stdout.write(self.style.WARNING('  삭제할 카테고리가 없습니다.'))
            
            self.stdout.write(self.style.SUCCESS('\n데이터베이스 초기화가 완료되었습니다.'))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  데이터 초기화 중 오류 발생: {e}')
            )
            return
        
        # 카테고리 데이터
        categories_data = [
            {
                'name': 'Network',
                'slug': 'network',
                'description': '네트워크 기초와 프로토콜을 배워봅시다',
                'order': 1,
            },
            {
                'name': 'Linux',
                'slug': 'linux',
                'description': 'Linux 시스템 운영과 관리',
                'order': 2,
            },
            {
                'name': 'Python',
                'slug': 'python',
                'description': '간단하고 강력한 프로그래밍 언어',
                'order': 3,
            },
            {
                'name': 'AWS',
                'slug': 'aws',
                'description': '아마존 웹 서비스 클라우드 플랫폼',
                'order': 4,
            },
        ]
        
        # 주제 데이터
        topics_data = initial_topics_data.topics_data
        
        # 카테고리 생성
        created_categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description'],
                    'order': cat_data['order'],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'카테고리 생성: {category.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'카테고리 이미 존재: {category.name}'))
            created_categories.append((cat_data['slug'], category))
        
        # 주제 생성
        topic_count = 0
        for category_slug, category in created_categories:
            if category_slug in topics_data:
                for topic_data in topics_data[category_slug]:
                    topic, created = Topic.objects.get_or_create(
                        category=category,
                        slug=topic_data['slug'],
                        defaults={
                            'title': topic_data['title'],
                            'content': topic_data['content'],
                            'order': topic_data['order'],
                        }
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'  주제 생성: {topic.title}'))
                        topic_count += 1
                    else:
                        self.stdout.write(self.style.WARNING(f'  주제 이미 존재: {topic.title}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n초기 데이터 로드 완료!'))
        self.stdout.write(self.style.SUCCESS(f'생성된 주제: {topic_count}개'))

        from django.core.cache import cache

        # 캐시 클리어
        self.stdout.write('\n캐시를 클리어합니다...')
        cache.clear()
        self.stdout.write(self.style.SUCCESS('캐시 클리어 완료!'))

