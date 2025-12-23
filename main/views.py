from django.shortcuts import render

def index(request):
    """메인 페이지"""
    categories = [
        {'name': 'Network', 'slug': 'network', 'description': '네트워크 기초와 프로토콜을 배워봅시다'},
        {'name': 'Linux', 'slug': 'linux', 'description': 'Linux 시스템 운영과 관리'},
        {'name': 'Python', 'slug': 'python', 'description': '간단하고 강력한 프로그래밍 언어'},
        {'name': 'AWS', 'slug': 'aws', 'description': '아마존 웹 서비스 클라우드 플랫폼'},
    ]
    context = {
        'categories': categories,
    }
    return render(request, 'main/index.html', context)

def tutorial(request, category):
    """카테고리별 튜토리얼 목록"""
    topics = {
        'network': [
            {'title': '네트워크 기초', 'slug': 'network-basics'},
            {'title': 'TCP/IP 프로토콜', 'slug': 'tcp-ip'},
            {'title': 'HTTP/HTTPS', 'slug': 'http-https'},
        ],
        'linux': [
            {'title': 'Linux 기초', 'slug': 'linux-basics'},
            {'title': '명령어 사용법', 'slug': 'commands'},
            {'title': '시스템 관리', 'slug': 'system-admin'},
        ],
        'python': [
            {'title': 'Python 기초', 'slug': 'python-basics'},
            {'title': '자료구조', 'slug': 'data-structures'},
            {'title': '함수와 클래스', 'slug': 'functions-classes'},
        ],
        'aws': [
            {'title': 'AWS 시작하기', 'slug': 'aws-getting-started'},
            {'title': 'EC2 인스턴스', 'slug': 'ec2'},
            {'title': 'S3 스토리지', 'slug': 's3'},
        ],
    }
    
    category_names = {
        'network': 'Network',
        'linux': 'Linux',
        'python': 'Python',
        'aws': 'AWS',
    }
    
    context = {
        'category': category,
        'category_name': category_names.get(category, category),
        'topics': topics.get(category, []),
    }
    return render(request, 'main/tutorial.html', context)

def topic_detail(request, category, topic):
    """주제 상세 페이지"""
    # 카테고리별 주제 목록 가져오기
    topics_dict = {
        'network': [
            {'title': '네트워크 기초', 'slug': 'network-basics'},
            {'title': 'TCP/IP 프로토콜', 'slug': 'tcp-ip'},
            {'title': 'HTTP/HTTPS', 'slug': 'http-https'},
        ],
        'linux': [
            {'title': 'Linux 기초', 'slug': 'linux-basics'},
            {'title': '명령어 사용법', 'slug': 'commands'},
            {'title': '시스템 관리', 'slug': 'system-admin'},
        ],
        'python': [
            {'title': 'Python 기초', 'slug': 'python-basics'},
            {'title': '자료구조', 'slug': 'data-structures'},
            {'title': '함수와 클래스', 'slug': 'functions-classes'},
        ],
        'aws': [
            {'title': 'AWS 시작하기', 'slug': 'aws-getting-started'},
            {'title': 'EC2 인스턴스', 'slug': 'ec2'},
            {'title': 'S3 스토리지', 'slug': 's3'},
        ],
    }
    
    category_names = {
        'network': 'Network',
        'linux': 'Linux',
        'python': 'Python',
        'aws': 'AWS',
    }
    
    content = {
        'network-basics': {
            'title': '네트워크 기초',
            'content': '<h1>네트워크란?</h1><p>네트워크는 두 개 이상의 컴퓨터나 장치가 서로 연결되어 데이터를 주고받을 수 있는 통신 시스템입니다.</p>'
        },
        'tcp-ip': {
            'title': 'TCP/IP 프로토콜',
            'content': '<h1>TCP/IP란?</h1><p>TCP/IP는 인터넷에서 사용되는 가장 중요한 통신 프로토콜 스위트입니다. TCP는 전송 제어 프로토콜, IP는 인터넷 프로토콜을 의미합니다.</p>'
        },
        'http-https': {
            'title': 'HTTP/HTTPS',
            'content': '<h1>HTTP/HTTPS란?</h1><p>HTTP는 웹 브라우저와 서버 간의 통신을 위한 프로토콜이며, HTTPS는 보안이 강화된 버전입니다.</p>'
        },
        'linux-basics': {
            'title': 'Linux 기초',
            'content': '<h1>Linux란?</h1><p>Linux는 오픈소스 운영체제로, 서버와 클라우드 환경에서 널리 사용됩니다.</p>'
        },
        'commands': {
            'title': '명령어 사용법',
            'content': '<h1>Linux 명령어</h1><p>Linux에서는 터미널을 통해 다양한 명령어를 사용하여 시스템을 제어할 수 있습니다.</p>'
        },
        'system-admin': {
            'title': '시스템 관리',
            'content': '<h1>시스템 관리</h1><p>Linux 시스템 관리에는 사용자 관리, 프로세스 관리, 파일 시스템 관리 등이 포함됩니다.</p>'
        },
        'python-basics': {
            'title': 'Python 기초',
            'content': '<h1>Python이란?</h1><p>Python은 간단하고 읽기 쉬운 문법을 가진 고급 프로그래밍 언어입니다.</p>'
        },
        'aws-getting-started': {
            'title': 'AWS 시작하기',
            'content': '<h1>AWS란?</h1><p>AWS(Amazon Web Services)는 아마존에서 제공하는 클라우드 컴퓨팅 플랫폼입니다.</p>'
        },
        'ec2': {
            'title': 'EC2 인스턴스',
            'content': '<h1>EC2란?</h1><p>EC2는 AWS의 가상 서버 서비스로, 클라우드에서 컴퓨팅 용량을 제공합니다.</p>'
        },
        's3': {
            'title': 'S3 스토리지',
            'content': '<h1>S3란?</h1><p>S3는 AWS의 객체 스토리지 서비스로, 대용량 데이터를 안전하게 저장할 수 있습니다.</p>'
        },
    }
    
    topic_data = content.get(topic, {
        'title': '주제',
        'content': '<p>내용이 준비 중입니다.</p>'
    })
    
    context = {
        'category': category,
        'category_name': category_names.get(category, category),
        'topic': topic,
        'title': topic_data['title'],
        'content': topic_data['content'],
        'topics': topics_dict.get(category, []),
    }
    return render(request, 'main/topic_detail.html', context)

