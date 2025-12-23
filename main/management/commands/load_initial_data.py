"""
초기 데이터 로드 커맨드
사용법: python manage.py load_initial_data
"""
from django.core.management.base import BaseCommand
from main.models import Category, Topic


class Command(BaseCommand):
    help = '초기 카테고리 및 주제 데이터를 데이터베이스에 로드합니다'

    def handle(self, *args, **options):
        self.stdout.write('초기 데이터 로드를 시작합니다...')
        
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
        topics_data = {
            'network': [
                {
                    'title': '네트워크 기초',
                    'slug': 'network-basics',
                    'content': '<h1>네트워크란?</h1><p>네트워크는 두 개 이상의 컴퓨터나 장치가 서로 연결되어 데이터를 주고받을 수 있는 통신 시스템입니다.</p>',
                    'order': 1,
                },
                {
                    'title': 'TCP/IP 프로토콜',
                    'slug': 'tcp-ip',
                    'content': '<h1>TCP/IP란?</h1><p>TCP/IP는 인터넷에서 사용되는 가장 중요한 통신 프로토콜 스위트입니다. TCP는 전송 제어 프로토콜, IP는 인터넷 프로토콜을 의미합니다.</p>',
                    'order': 2,
                },
                {
                    'title': 'HTTP/HTTPS',
                    'slug': 'http-https',
                    'content': '<h1>HTTP/HTTPS란?</h1><p>HTTP는 웹 브라우저와 서버 간의 통신을 위한 프로토콜이며, HTTPS는 보안이 강화된 버전입니다.</p>',
                    'order': 3,
                },
            ],
            'linux': [
                {
                    'title': 'Linux 기초',
                    'slug': 'linux-basics',
                    'content': '<h1>Linux란?</h1><p>Linux는 오픈소스 운영체제로, 서버와 클라우드 환경에서 널리 사용됩니다.</p>',
                    'order': 1,
                },
                {
                    'title': '명령어 사용법',
                    'slug': 'commands',
                    'content': '<h1>Linux 명령어</h1><p>Linux에서는 터미널을 통해 다양한 명령어를 사용하여 시스템을 제어할 수 있습니다.</p>',
                    'order': 2,
                },
                {
                    'title': '시스템 관리',
                    'slug': 'system-admin',
                    'content': '<h1>시스템 관리</h1><p>Linux 시스템 관리에는 사용자 관리, 프로세스 관리, 파일 시스템 관리 등이 포함됩니다.</p>',
                    'order': 3,
                },
            ],
            'python': [
                {
                    'title': 'Python 기초',
                    'slug': 'python-basics',
                    'content': '<h1>Python이란?</h1><p>Python은 간단하고 읽기 쉬운 문법을 가진 고급 프로그래밍 언어입니다.</p>',
                    'order': 1,
                },
                {
                    'title': '자료구조',
                    'slug': 'data-structures',
                    'content': '<p>내용이 준비 중입니다.</p>',
                    'order': 2,
                },
                {
                    'title': '함수와 클래스',
                    'slug': 'functions-classes',
                    'content': '<p>내용이 준비 중입니다.</p>',
                    'order': 3,
                },
            ],
            'aws': [
                {
                    'title': 'AWS 시작하기',
                    'slug': 'aws-getting-started',
                    'content': '<h1>AWS란?</h1><p>AWS(Amazon Web Services)는 아마존에서 제공하는 클라우드 컴퓨팅 플랫폼입니다.</p>',
                    'order': 1,
                },
                {
                    'title': 'EC2 인스턴스',
                    'slug': 'ec2',
                    'content': '<h1>EC2란?</h1><p>EC2는 AWS의 가상 서버 서비스로, 클라우드에서 컴퓨팅 용량을 제공합니다.</p>',
                    'order': 2,
                },
                {
                    'title': 'S3 스토리지',
                    'slug': 's3',
                    'content': '<h1>S3란?</h1><p>S3는 AWS의 객체 스토리지 서비스로, 대용량 데이터를 안전하게 저장할 수 있습니다.</p>',
                    'order': 3,
                },
            ],
        }
        
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

