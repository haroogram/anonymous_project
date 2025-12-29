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
        
        # 기존의 불필요한 주제 삭제 (data-structures, functions-classes)
        self.stdout.write('\n기존 불필요한 주제를 삭제합니다...')
        slugs_to_delete = ['data-structures', 'functions-classes']
        for slug in slugs_to_delete:
            try:
                topics = Topic.objects.filter(slug=slug)
                count = topics.count()
                if count > 0:
                    for topic in topics:
                        self.stdout.write(
                            f"  삭제: {topic.title} (slug: {topic.slug}, "
                            f"카테고리: {topic.category.name})"
                        )
                    topics.delete()
                    self.stdout.write(
                        self.style.SUCCESS(f"  '{slug}' slug를 가진 {count}개의 주제가 삭제되었습니다.")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"  slug '{slug}'를 가진 주제를 찾을 수 없습니다.")
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  '{slug}' 삭제 중 오류 발생: {e}")
                )
        
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
                    'title': '표준입력',
                    'slug': 'standard-input',
                    'content': '''<h1>표준입력 (Standard Input)</h1>
<p>Python에서 사용자로부터 데이터를 입력받는 방법을 알아봅시다.</p>

<h2>input() 함수</h2>
<p><code>input()</code> 함수는 사용자로부터 문자열을 입력받습니다. 항상 문자열(str) 타입으로 반환됩니다.</p>

<pre><code># 기본 사용법
name = input("이름을 입력하세요: ")
print(f"안녕하세요, {name}님!")

# 숫자 입력받기
age = int(input("나이를 입력하세요: "))
print(f"당신은 {age}세입니다.")
</code></pre>

<h2>주의사항</h2>
<ul>
    <li><code>input()</code>은 항상 문자열을 반환하므로, 숫자를 입력받으려면 <code>int()</code>나 <code>float()</code>로 변환해야 합니다.</li>
    <li>입력이 완료될 때까지 프로그램이 대기합니다.</li>
</ul>''',
                    'order': 1,
                },
                {
                    'title': '연산자',
                    'slug': 'operators',
                    'content': '''<h1>연산자 (Operators)</h1>
<p>Python에서 사용하는 다양한 연산자에 대해 알아봅시다.</p>

<h2>산술 연산자</h2>
<pre><code>a = 10
b = 3

print(a + b)  # 덧셈: 13
print(a - b)  # 뺄셈: 7
print(a * b)  # 곱셈: 30
print(a / b)  # 나눗셈: 3.333...
print(a // b) # 몫: 3
print(a % b)  # 나머지: 1
print(a ** b) # 거듭제곱: 1000
</code></pre>

<h2>비교 연산자</h2>
<pre><code>a = 10
b = 20

print(a == b)  # 같음: False
print(a != b)  # 다름: True
print(a < b)   # 작음: True
print(a > b)   # 큼: False
print(a <= b)  # 작거나 같음: True
print(a >= b)  # 크거나 같음: False
</code></pre>

<h2>논리 연산자</h2>
<pre><code>x = True
y = False

print(x and y)  # AND: False
print(x or y)   # OR: True
print(not x)    # NOT: False
</code></pre>

<h2>할당 연산자</h2>
<pre><code>a = 10
a += 5   # a = a + 5와 같음 (15)
a -= 3   # a = a - 3과 같음 (12)
a *= 2   # a = a * 2와 같음 (24)
a /= 4   # a = a / 4와 같음 (6.0)
</code></pre>''',
                    'order': 2,
                },
                {
                    'title': 'if',
                    'slug': 'if-statement',
                    'content': '''<h1>if 문 (조건문)</h1>
<p>조건에 따라 코드를 실행하는 방법을 알아봅시다.</p>

<h2>기본 if 문</h2>
<pre><code>age = 20

if age >= 18:
    print("성인입니다.")
</code></pre>

<h2>if-else 문</h2>
<pre><code>age = 15

if age >= 18:
    print("성인입니다.")
else:
    print("미성년자입니다.")
</code></pre>

<h2>if-elif-else 문</h2>
<pre><code>score = 85

if score >= 90:
    print("A등급")
elif score >= 80:
    print("B등급")
elif score >= 70:
    print("C등급")
else:
    print("D등급")
</code></pre>

<h2>중첩 if 문</h2>
<pre><code>age = 25
has_license = True

if age >= 18:
    if has_license:
        print("운전 가능합니다.")
    else:
        print("면허가 필요합니다.")
else:
    print("미성년자는 운전할 수 없습니다.")
</code></pre>

<h2>조건 표현식 (삼항 연산자)</h2>
<pre><code>age = 20
status = "성인" if age >= 18 else "미성년자"
print(status)
</code></pre>''',
                    'order': 3,
                },
                {
                    'title': 'for',
                    'slug': 'for-loop',
                    'content': '''<h1>for 루프 (반복문)</h1>
<p>코드를 반복해서 실행하는 방법을 알아봅시다.</p>

<h2>기본 for 루프</h2>
<pre><code># 리스트 반복
fruits = ["사과", "바나나", "오렌지"]
for fruit in fruits:
    print(fruit)
</code></pre>

<h2>range() 함수와 함께 사용</h2>
<pre><code># 0부터 4까지
for i in range(5):
    print(i)  # 0, 1, 2, 3, 4

# 1부터 10까지
for i in range(1, 11):
    print(i)

# 0부터 10까지 2씩 증가
for i in range(0, 11, 2):
    print(i)  # 0, 2, 4, 6, 8, 10
</code></pre>

<h2>문자열 반복</h2>
<pre><code>message = "안녕하세요"
for char in message:
    print(char)
</code></pre>

<h2>enumerate()로 인덱스와 값 함께 사용</h2>
<pre><code>fruits = ["사과", "바나나", "오렌지"]
for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")
</code></pre>

<h2>딕셔너리 반복</h2>
<pre><code>person = {"이름": "홍길동", "나이": 30, "직업": "개발자"}

# 키만 반복
for key in person:
    print(key)

# 값만 반복
for value in person.values():
    print(value)

# 키와 값 함께 반복
for key, value in person.items():
    print(f"{key}: {value}")
</code></pre>

<h2>중첩 for 루프</h2>
<pre><code>for i in range(3):
    for j in range(2):
        print(f"({i}, {j})")
</code></pre>

<h2>break와 continue</h2>
<pre><code># break: 루프 중단
for i in range(10):
    if i == 5:
        break
    print(i)  # 0, 1, 2, 3, 4

# continue: 다음 반복으로 건너뛰기
for i in range(10):
    if i % 2 == 0:
        continue
    print(i)  # 1, 3, 5, 7, 9
</code></pre>''',
                    'order': 4,
                },
                {
                    'title': 'while',
                    'slug': 'while-loop',
                    'content': '''<h1>while 루프 (반복문)</h1>
<p>조건이 만족되는 동안 코드를 반복 실행하는 방법을 알아봅시다.</p>

<h2>기본 while 루프</h2>
<pre><code>count = 0
while count < 5:
    print(count)
    count += 1
</code></pre>

<h2>무한 루프와 break</h2>
<pre><code>while True:
    user_input = input("종료하려면 'q'를 입력하세요: ")
    if user_input == 'q':
        break
    print(f"입력한 값: {user_input}")
</code></pre>

<h2>continue 사용</h2>
<pre><code>num = 0
while num < 10:
    num += 1
    if num % 2 == 0:
        continue
    print(num)  # 1, 3, 5, 7, 9
</code></pre>

<h2>else 절 사용</h2>
<p>while 루프에서 else 절은 break로 루프가 중단되지 않고 정상적으로 종료될 때 실행됩니다.</p>
<pre><code>count = 0
while count < 5:
    print(count)
    count += 1
else:
    print("루프가 정상적으로 종료되었습니다.")
</code></pre>

<h2>실용 예제</h2>
<pre><code># 사용자 입력 검증
password = ""
while len(password) < 8:
    password = input("비밀번호를 입력하세요 (최소 8자): ")
    if len(password) < 8:
        print("비밀번호는 최소 8자 이상이어야 합니다.")
print("비밀번호가 설정되었습니다!")

# 숫자 맞추기 게임
import random
target = random.randint(1, 100)
guess = 0
attempts = 0

while guess != target:
    guess = int(input("1부터 100까지 숫자를 맞춰보세요: "))
    attempts += 1
    if guess < target:
        print("더 큰 수입니다.")
    elif guess > target:
        print("더 작은 수입니다.")
    else:
        print(f"정답입니다! {attempts}번 만에 맞췄습니다.")
</code></pre>''',
                    'order': 5,
                },
                {
                    'title': '함수',
                    'slug': 'functions',
                    'content': '''<h1>함수 (Functions)</h1>
<p>코드를 재사용할 수 있도록 함수로 만드는 방법을 알아봅시다.</p>

<h2>기본 함수 정의</h2>
<pre><code>def greet():
    print("안녕하세요!")

greet()  # 함수 호출
</code></pre>

<h2>매개변수가 있는 함수</h2>
<pre><code>def greet(name):
    print(f"안녕하세요, {name}님!")

greet("홍길동")
</code></pre>

<h2>반환값이 있는 함수</h2>
<pre><code>def add(a, b):
    return a + b

result = add(3, 5)
print(result)  # 8
</code></pre>

<h2>기본값 매개변수</h2>
<pre><code>def greet(name, greeting="안녕하세요"):
    print(f"{greeting}, {name}님!")

greet("홍길동")  # 안녕하세요, 홍길동님!
greet("홍길동", "안녕")  # 안녕, 홍길동님!
</code></pre>

<h2>키워드 인수</h2>
<pre><code>def introduce(name, age, city):
    print(f"이름: {name}, 나이: {age}, 거주지: {city}")

introduce(age=30, city="서울", name="홍길동")
</code></pre>

<h2>가변 인수</h2>
<pre><code># *args: 여러 개의 위치 인수
def sum_all(*args):
    total = 0
    for num in args:
        total += num
    return total

print(sum_all(1, 2, 3, 4, 5))  # 15

# **kwargs: 여러 개의 키워드 인수
def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_info(name="홍길동", age=30, city="서울")
</code></pre>

<h2>람다 함수</h2>
<pre><code># 간단한 함수를 한 줄로 표현
add = lambda x, y: x + y
print(add(3, 5))  # 8

# map, filter 등과 함께 사용
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x**2, numbers))
print(squared)  # [1, 4, 9, 16, 25]
</code></pre>

<h2>함수 내 변수 스코프</h2>
<pre><code># 전역 변수
x = 10

def my_function():
    # 지역 변수
    x = 20
    print(f"함수 내부: {x}")  # 20

my_function()
print(f"함수 외부: {x}")  # 10

# global 키워드로 전역 변수 수정
def change_global():
    global x
    x = 30

change_global()
print(x)  # 30
</code></pre>

<h2>문서화 (docstring)</h2>
<pre><code>def calculate_area(radius):
    """
    원의 넓이를 계산합니다.
    
    Args:
        radius (float): 원의 반지름
    
    Returns:
        float: 원의 넓이
    """
    return 3.14159 * radius ** 2
</code></pre>''',
                    'order': 6,
                },
                {
                    'title': '리스트',
                    'slug': 'lists',
                    'content': '''<h1>리스트 (Lists)</h1>
<p>여러 개의 값을 순서대로 저장하는 자료구조입니다.</p>

<h2>리스트 생성</h2>
<pre><code># 빈 리스트
my_list = []

# 값이 있는 리스트
fruits = ["사과", "바나나", "오렌지"]
numbers = [1, 2, 3, 4, 5]

# 다양한 타입 혼합 가능
mixed = [1, "문자열", 3.14, True]
</code></pre>

<h2>인덱싱과 슬라이싱</h2>
<pre><code>fruits = ["사과", "바나나", "오렌지", "포도"]

# 인덱싱
print(fruits[0])    # 사과 (첫 번째 요소)
print(fruits[-1])   # 포도 (마지막 요소)

# 슬라이싱
print(fruits[1:3])     # ["바나나", "오렌지"]
print(fruits[:2])      # ["사과", "바나나"]
print(fruits[2:])      # ["오렌지", "포도"]
print(fruits[::2])     # ["사과", "오렌지"] (2칸씩)
</code></pre>

<h2>리스트 메서드</h2>
<pre><code>fruits = ["사과", "바나나"]

# 요소 추가
fruits.append("오렌지")  # 맨 끝에 추가
fruits.insert(1, "포도")  # 특정 위치에 삽입
fruits.extend(["체리", "망고"])  # 여러 요소 추가

# 요소 제거
fruits.remove("바나나")  # 값으로 제거
popped = fruits.pop()    # 마지막 요소 제거 및 반환
popped = fruits.pop(0)   # 특정 인덱스 요소 제거

# 검색
index = fruits.index("사과")  # 인덱스 찾기
count = fruits.count("사과")  # 개수 세기

# 정렬
numbers = [3, 1, 4, 1, 5]
numbers.sort()           # 오름차순 정렬 (원본 수정)
sorted_nums = sorted(numbers)  # 정렬된 새 리스트 반환
numbers.reverse()        # 역순 정렬

# 기타
fruits.clear()           # 모든 요소 제거
fruits.copy()            # 복사본 생성
</code></pre>

<h2>리스트 컴프리헨션</h2>
<pre><code># 기본 문법
squares = [x**2 for x in range(10)]
# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# 조건문 포함
evens = [x for x in range(20) if x % 2 == 0]
# [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

# 중첩 루프
matrix = [[i*j for j in range(3)] for i in range(3)]
# [[0, 0, 0], [0, 1, 2], [0, 2, 4]]
</code></pre>

<h2>리스트 연산</h2>
<pre><code>list1 = [1, 2, 3]
list2 = [4, 5, 6]

# 연결
combined = list1 + list2  # [1, 2, 3, 4, 5, 6]

# 반복
repeated = list1 * 3  # [1, 2, 3, 1, 2, 3, 1, 2, 3]

# 멤버십 테스트
print(2 in list1)  # True
print(5 in list1)  # False
</code></pre>

<h2>다차원 리스트</h2>
<pre><code># 2차원 리스트 (행렬)
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

print(matrix[1][2])  # 6 (2행 3열)

# 요소 접근
for row in matrix:
    for element in row:
        print(element, end=" ")
    print()
</code></pre>''',
                    'order': 7,
                },
                {
                    'title': '튜플/딕셔너리/셋',
                    'slug': 'tuple-dict-set',
                    'content': '''<h1>튜플, 딕셔너리, 셋</h1>
<p>Python의 다른 중요한 자료구조들을 알아봅시다.</p>

<h2>튜플 (Tuple)</h2>
<p>튜플은 불변(immutable) 순서가 있는 자료구조입니다.</p>
<pre><code># 튜플 생성
my_tuple = (1, 2, 3)
my_tuple = 1, 2, 3  # 괄호 생략 가능

# 단일 요소 튜플 (쉼표 필요)
single = (1,)

# 인덱싱
print(my_tuple[0])   # 1
print(my_tuple[-1])  # 3

# 튜플 언패킹
a, b, c = my_tuple
print(a, b, c)  # 1 2 3

# 튜플 메서드
numbers = (1, 2, 2, 3)
count = numbers.count(2)  # 2 (개수)
index = numbers.index(3)  # 3 (인덱스)
</code></pre>

<h2>딕셔너리 (Dictionary)</h2>
<p>키-값 쌍으로 데이터를 저장하는 자료구조입니다.</p>
<pre><code># 딕셔너리 생성
person = {
    "name": "홍길동",
    "age": 30,
    "city": "서울"
}

# 또는
person = dict(name="홍길동", age=30, city="서울")

# 요소 접근
print(person["name"])  # 홍길동
print(person.get("age"))  # 30 (키가 없으면 None 반환)
print(person.get("email", "없음"))  # 기본값 반환

# 요소 추가/수정
person["email"] = "hong@example.com"
person["age"] = 31

# 요소 제거
del person["city"]
email = person.pop("email")  # 제거 및 값 반환

# 딕셔너리 메서드
keys = person.keys()      # 키 목록
values = person.values()  # 값 목록
items = person.items()    # (키, 값) 쌍 목록

# 딕셔너리 컴프리헨션
squares = {x: x**2 for x in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# 중첩 딕셔너리
students = {
    "student1": {"name": "홍길동", "age": 20},
    "student2": {"name": "김철수", "age": 21}
}
</code></pre>

<h2>셋 (Set)</h2>
<p>셋은 중복되지 않는 고유한 요소들의 집합입니다.</p>
<pre><code># 셋 생성
my_set = {1, 2, 3, 3, 4}  # {1, 2, 3, 4} (중복 제거)
my_set = set([1, 2, 3])

# 빈 셋 (주의: {}는 딕셔너리)
empty_set = set()

# 요소 추가/제거
my_set.add(5)
my_set.remove(3)      # 요소가 없으면 에러
my_set.discard(3)     # 요소가 없어도 에러 안남
popped = my_set.pop() # 임의의 요소 제거 및 반환

# 셋 연산
set1 = {1, 2, 3, 4}
set2 = {3, 4, 5, 6}

union = set1 | set2           # 합집합: {1, 2, 3, 4, 5, 6}
intersection = set1 & set2    # 교집합: {3, 4}
difference = set1 - set2      # 차집합: {1, 2}
symmetric_diff = set1 ^ set2  # 대칭 차집합: {1, 2, 5, 6}

# 멤버십 테스트
print(2 in set1)  # True

# 셋 메서드
set1.update(set2)      # 합집합으로 업데이트
set1.intersection_update(set2)  # 교집합으로 업데이트

# 부분집합 확인
print(set1.issubset(set2))     # False
print(set1.issuperset({1, 2})) # True
</code></pre>

<h2>자료구조 간 변환</h2>
<pre><code># 리스트 → 셋 (중복 제거)
my_list = [1, 2, 2, 3, 3]
my_set = set(my_list)  # {1, 2, 3}

# 셋 → 리스트
unique_list = list(my_set)

# 리스트 → 튜플
my_tuple = tuple(my_list)

# 딕셔너리 → 리스트
person = {"name": "홍길동", "age": 30}
keys_list = list(person.keys())
values_list = list(person.values())
</code></pre>''',
                    'order': 8,
                },
                {
                    'title': '컴프리헨션',
                    'slug': 'comprehensions',
                    'content': '''<h1>컴프리헨션 (Comprehensions)</h1>
<p>리스트, 딕셔너리, 셋을 간결하게 생성하는 Python의 강력한 기능입니다.</p>

<h2>리스트 컴프리헨션</h2>
<pre><code># 기본 문법: [표현식 for 항목 in 반복가능객체]

# 예제 1: 0부터 9까지 제곱
squares = [x**2 for x in range(10)]
# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# 예제 2: 문자열 리스트
words = ["hello", "world", "python"]
uppercase = [word.upper() for word in words]
# ["HELLO", "WORLD", "PYTHON"]

# 예제 3: 조건문 포함 (if)
evens = [x for x in range(20) if x % 2 == 0]
# [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

# 예제 4: 조건문 포함 (if-else)
result = [x if x % 2 == 0 else -x for x in range(10)]
# [0, -1, 2, -3, 4, -5, 6, -7, 8, -9]

# 예제 5: 중첩 루프
matrix = [[i*j for j in range(3)] for i in range(3)]
# [[0, 0, 0], [0, 1, 2], [0, 2, 4]]

# 예제 6: 평면화 (flatten)
nested = [[1, 2, 3], [4, 5], [6, 7, 8, 9]]
flat = [item for sublist in nested for item in sublist]
# [1, 2, 3, 4, 5, 6, 7, 8, 9]
</code></pre>

<h2>딕셔너리 컴프리헨션</h2>
<pre><code># 기본 문법: {키: 값 for 항목 in 반복가능객체}

# 예제 1: 숫자와 제곱값
squares = {x: x**2 for x in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# 예제 2: 딕셔너리 변환
original = {"a": 1, "b": 2, "c": 3}
doubled = {k: v*2 for k, v in original.items()}
# {"a": 2, "b": 4, "c": 6}

# 예제 3: 조건문 포함
filtered = {k: v for k, v in original.items() if v > 1}
# {"b": 2, "c": 3}

# 예제 4: 키와 값 교환
reversed_dict = {v: k for k, v in original.items()}
# {1: "a", 2: "b", 3: "c"}
</code></pre>

<h2>셋 컴프리헨션</h2>
<pre><code># 기본 문법: {표현식 for 항목 in 반복가능객체}

# 예제 1: 중복 제거
numbers = [1, 2, 2, 3, 3, 4, 5]
unique = {x for x in numbers}
# {1, 2, 3, 4, 5}

# 예제 2: 제곱값
squares = {x**2 for x in range(10)}
# {0, 1, 64, 4, 36, 9, 16, 49, 25, 81}

# 예제 3: 조건문 포함
evens = {x for x in range(20) if x % 2 == 0}
# {0, 2, 4, 6, 8, 10, 12, 14, 16, 18}
</code></pre>

<h2>컴프리헨션의 장점</h2>
<ul>
    <li><strong>간결함</strong>: 여러 줄의 코드를 한 줄로 표현</li>
    <li><strong>가독성</strong>: 의도가 명확하게 드러남</li>
    <li><strong>성능</strong>: 일반적으로 for 루프보다 빠름</li>
</ul>

<h2>주의사항</h2>
<ul>
    <li>복잡한 로직에는 일반 for 루프가 더 읽기 쉬울 수 있습니다.</li>
    <li>너무 중첩된 컴프리헨션은 가독성을 해칩니다.</li>
    <li>부작용(side effect)이 필요한 경우에는 일반 루프를 사용하세요.</li>
</ul>

<h2>실용 예제</h2>
<pre><code># 파일 목록에서 확장자 추출
files = ["app.py", "config.txt", "readme.md"]
extensions = {f.split(".")[-1] for f in files}
# {"py", "txt", "md"}

# 단어 길이별 그룹화
words = ["apple", "banana", "cat", "dog", "elephant"]
word_groups = {len(word): [w for w in words if len(w) == len(word)] 
               for word in words}
# {5: ["apple"], 6: ["banana"], 3: ["cat", "dog"], 8: ["elephant"]}
</code></pre>''',
                    'order': 9,
                },
                {
                    'title': '파일입출력',
                    'slug': 'file-io',
                    'content': '''<h1>파일 입출력 (File I/O)</h1>
<p>파일을 읽고 쓰는 방법을 알아봅시다.</p>

<h2>파일 쓰기</h2>
<pre><code># 기본 파일 쓰기
with open("example.txt", "w", encoding="utf-8") as f:
    f.write("안녕하세요!")
    f.write("\\nPython 파일 입출력입니다.")

# 여러 줄 쓰기
with open("example.txt", "w", encoding="utf-8") as f:
    f.writelines(["첫 번째 줄\\n", "두 번째 줄\\n", "세 번째 줄\\n"])

# print 함수로 파일에 쓰기
with open("example.txt", "w", encoding="utf-8") as f:
    print("Hello, World!", file=f)
    print("Python Programming", file=f)
</code></pre>

<h2>파일 읽기</h2>
<pre><code># 전체 파일 읽기
with open("example.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print(content)

# 한 줄씩 읽기
with open("example.txt", "r", encoding="utf-8") as f:
    line = f.readline()
    while line:
        print(line.strip())  # strip()으로 줄바꿈 제거
        line = f.readline()

# 모든 줄을 리스트로 읽기
with open("example.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()
    for line in lines:
        print(line.strip())

# 파일 객체를 직접 반복 (권장)
with open("example.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(line.strip())
</code></pre>

<h2>파일 모드</h2>
<pre><code>"r"   # 읽기 모드 (기본값)
"w"   # 쓰기 모드 (파일이 있으면 덮어씀)
"x"   # 배타적 생성 모드 (파일이 있으면 에러)
"a"   # 추가 모드 (파일 끝에 추가)
"b"   # 바이너리 모드 (이미지, 비디오 등)
"t"   # 텍스트 모드 (기본값)
"+"   # 읽기/쓰기 모두 가능

# 조합
"r+"  # 읽기/쓰기
"w+"  # 쓰기/읽기 (파일이 있으면 덮어씀)
"a+"  # 추가/읽기
</code></pre>

<h2>파일 추가 모드</h2>
<pre><code># 파일 끝에 내용 추가
with open("example.txt", "a", encoding="utf-8") as f:
    f.write("\\n추가된 내용입니다.")
</code></pre>

<h2>CSV 파일 처리</h2>
<pre><code>import csv

# CSV 파일 쓰기
with open("data.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["이름", "나이", "도시"])
    writer.writerow(["홍길동", 30, "서울"])
    writer.writerow(["김철수", 25, "부산"])

# CSV 파일 읽기
with open("data.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)

# 딕셔너리 형태로 CSV 읽기
with open("data.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"{row['이름']}: {row['나이']}세, {row['도시']}")
</code></pre>

<h2>JSON 파일 처리</h2>
<pre><code>import json

# JSON 파일 쓰기
data = {
    "name": "홍길동",
    "age": 30,
    "city": "서울",
    "hobbies": ["독서", "영화감상"]
}

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# JSON 파일 읽기
with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    print(data)
</code></pre>

<h2>파일 및 디렉토리 관리</h2>
<pre><code>import os

# 파일 존재 확인
if os.path.exists("example.txt"):
    print("파일이 존재합니다.")

# 파일 삭제
os.remove("example.txt")

# 파일 이름 변경
os.rename("old.txt", "new.txt")

# 현재 작업 디렉토리
current_dir = os.getcwd()

# 디렉토리 목록
files = os.listdir(".")
</code></pre>

<h2>with 문 사용의 장점</h2>
<ul>
    <li>파일을 자동으로 닫아줌 (예외 발생 시에도)</li>
    <li>코드가 더 간결하고 안전함</li>
    <li>리소스 관리가 명확함</li>
</ul>''',
                    'order': 10,
                },
                {
                    'title': '클래스(객체지향)',
                    'slug': 'classes',
                    'content': '''<h1>클래스와 객체지향 프로그래밍</h1>
<p>객체지향 프로그래밍의 핵심인 클래스와 객체를 알아봅시다.</p>

<h2>기본 클래스 정의</h2>
<pre><code>class Person:
    # 클래스 변수
    species = "Homo sapiens"
    
    # 생성자 (__init__)
    def __init__(self, name, age):
        # 인스턴스 변수
        self.name = name
        self.age = age
    
    # 인스턴스 메서드
    def introduce(self):
        return f"안녕하세요, 저는 {self.name}이고 {self.age}세입니다."
    
    # 인스턴스 메서드
    def have_birthday(self):
        self.age += 1
        return f"생일 축하합니다! {self.age}세가 되었습니다."

# 객체 생성 및 사용
person1 = Person("홍길동", 30)
print(person1.introduce())
print(person1.have_birthday())
</code></pre>

<h2>클래스 변수 vs 인스턴스 변수</h2>
<pre><code>class Dog:
    # 클래스 변수
    species = "Canis familiaris"
    count = 0
    
    def __init__(self, name, breed):
        # 인스턴스 변수
        self.name = name
        self.breed = breed
        Dog.count += 1  # 클래스 변수 수정
    
    @classmethod
    def get_count(cls):
        return cls.count

dog1 = Dog("바둑이", "골든 리트리버")
dog2 = Dog("흰둥이", "불독")

print(Dog.species)  # 클래스 변수 접근
print(Dog.get_count())  # 2
</code></pre>

<h2>클래스 메서드와 정적 메서드</h2>
<pre><code>class Math:
    PI = 3.14159
    
    @classmethod
    def circle_area(cls, radius):
        return cls.PI * radius ** 2
    
    @staticmethod
    def add(a, b):
        return a + b

# 클래스 메서드 호출
area = Math.circle_area(5)

# 정적 메서드 호출
result = Math.add(3, 5)
</code></pre>

<h2>상속 (Inheritance)</h2>
<pre><code>class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        return "동물이 소리를 냅니다."

class Dog(Animal):
    def speak(self):
        return f"{self.name}가 멍멍 짖습니다."

class Cat(Animal):
    def speak(self):
        return f"{self.name}가 야옹 웁니다."

dog = Dog("바둑이")
cat = Cat("나비")

print(dog.speak())  # 바둑이가 멍멍 짖습니다.
print(cat.speak())  # 나비가 야옹 웁니다.
</code></pre>

<h2>super() 사용</h2>
<pre><code>class Animal:
    def __init__(self, name, species):
        self.name = name
        self.species = species

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name, "Dog")  # 부모 클래스 초기화
        self.breed = breed
</code></pre>

<h2>캡슐화 (Encapsulation)</h2>
<pre><code>class BankAccount:
    def __init__(self, balance):
        self.__balance = balance  # private 변수 (이름 앞에 __)
    
    def deposit(self, amount):
        if amount > 0:
            self.__balance += amount
            return f"{amount}원 입금되었습니다."
        return "입금 금액은 0보다 커야 합니다."
    
    def withdraw(self, amount):
        if 0 < amount <= self.__balance:
            self.__balance -= amount
            return f"{amount}원 출금되었습니다."
        return "잔액이 부족하거나 잘못된 금액입니다."
    
    def get_balance(self):
        return self.__balance

account = BankAccount(10000)
print(account.deposit(5000))
print(account.withdraw(3000))
print(f"잔액: {account.get_balance()}원")
</code></pre>

<h2>특수 메서드 (Magic Methods)</h2>
<pre><code>class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __str__(self):
        return f"Point({self.x}, {self.y})"
    
    def __repr__(self):
        return f"Point(x={self.x}, y={self.y})"
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

p1 = Point(1, 2)
p2 = Point(3, 4)
print(p1)  # Point(1, 2)
print(p1 == p2)  # False
print(p1 + p2)  # Point(4, 6)
</code></pre>

<h2>프로퍼티 (Property)</h2>
<pre><code>class Circle:
    def __init__(self, radius):
        self._radius = radius
    
    @property
    def radius(self):
        return self._radius
    
    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("반지름은 0 이상이어야 합니다.")
        self._radius = value
    
    @property
    def area(self):
        return 3.14159 * self._radius ** 2

circle = Circle(5)
print(circle.radius)  # 5
print(circle.area)    # 78.53975
circle.radius = 10
print(circle.area)    # 314.159
</code></pre>''',
                    'order': 11,
                },
                {
                    'title': 'DB연동',
                    'slug': 'db-connection',
                    'content': '''<h1>데이터베이스 연동</h1>
<p>Python에서 데이터베이스를 사용하는 방법을 알아봅시다.</p>

<h2>SQLite 기본 사용</h2>
<pre><code>import sqlite3

# 데이터베이스 연결
conn = sqlite3.connect("example.db")
cursor = conn.cursor()

# 테이블 생성
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        age INTEGER
    )
""")

# 데이터 삽입
cursor.execute("""
    INSERT INTO users (name, email, age)
    VALUES (?, ?, ?)
""", ("홍길동", "hong@example.com", 30))

# 여러 데이터 삽입
users_data = [
    ("김철수", "kim@example.com", 25),
    ("이영희", "lee@example.com", 28),
    ("박민수", "park@example.com", 32)
]
cursor.executemany("""
    INSERT INTO users (name, email, age)
    VALUES (?, ?, ?)
""", users_data)

# 변경사항 저장
conn.commit()

# 데이터 조회
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()
for row in rows:
    print(row)

# 조건 조회
cursor.execute("SELECT * FROM users WHERE age > ?", (25,))
results = cursor.fetchall()

# 딕셔너리 형태로 조회
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("SELECT * FROM users")
for row in cursor:
    print(dict(row))

# 연결 종료
conn.close()
</code></pre>

<h2>컨텍스트 매니저 사용</h2>
<pre><code>import sqlite3

with sqlite3.connect("example.db") as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
    # 자동으로 commit 및 close
</code></pre>

<h2>MySQL/MariaDB 연동 (mysql-connector-python)</h2>
<pre><code>import mysql.connector
from mysql.connector import Error

try:
    # 데이터베이스 연결
    connection = mysql.connector.connect(
        host="localhost",
        database="mydb",
        user="username",
        password="password"
    )
    
    if connection.is_connected():
        cursor = connection.cursor()
        
        # 데이터 조회
        cursor.execute("SELECT * FROM users")
        records = cursor.fetchall()
        
        for record in records:
            print(record)
        
        # 데이터 삽입
        cursor.execute("""
            INSERT INTO users (name, email, age)
            VALUES (%s, %s, %s)
        """, ("홍길동", "hong@example.com", 30))
        
        connection.commit()

except Error as e:
    print(f"데이터베이스 오류: {e}")

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
</code></pre>

<h2>PostgreSQL 연동 (psycopg2)</h2>
<pre><code>import psycopg2

try:
    connection = psycopg2.connect(
        host="localhost",
        database="mydb",
        user="username",
        password="password"
    )
    
    cursor = connection.cursor()
    
    # 데이터 조회
    cursor.execute("SELECT * FROM users")
    records = cursor.fetchall()
    
    # 데이터 삽입 (PostgreSQL은 %s 사용)
    cursor.execute("""
        INSERT INTO users (name, email, age)
        VALUES (%s, %s, %s)
    """, ("홍길동", "hong@example.com", 30))
    
    connection.commit()

except Exception as e:
    print(f"오류 발생: {e}")
    connection.rollback()

finally:
    cursor.close()
    connection.close()
</code></pre>

<h2>SQLAlchemy ORM 사용</h2>
<pre><code>from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# 모델 정의
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True)
    age = Column(Integer)
    
    def __repr__(self):
        return f"<User(name={self.name}, email={self.email})>"

# 데이터베이스 연결
engine = create_engine("sqlite:///example.db")
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# 데이터 삽입
new_user = User(name="홍길동", email="hong@example.com", age=30)
session.add(new_user)
session.commit()

# 데이터 조회
users = session.query(User).all()
for user in users:
    print(user)

# 조건 조회
user = session.query(User).filter(User.name == "홍길동").first()

# 데이터 수정
user.age = 31
session.commit()

# 데이터 삭제
session.delete(user)
session.commit()

session.close()
</code></pre>

<h2>주요 데이터베이스 라이브러리</h2>
<ul>
    <li><strong>sqlite3</strong>: Python 표준 라이브러리 (SQLite 전용)</li>
    <li><strong>mysql-connector-python</strong>: MySQL/MariaDB 공식 드라이버</li>
    <li><strong>pymysql</strong>: 순수 Python MySQL 클라이언트</li>
    <li><strong>psycopg2</strong>: PostgreSQL 드라이버</li>
    <li><strong>SQLAlchemy</strong>: ORM 및 SQL 툴킷</li>
</ul>

<h2>주의사항</h2>
<ul>
    <li>SQL 인젝션을 방지하기 위해 항상 파라미터화된 쿼리를 사용하세요.</li>
    <li>데이터베이스 연결은 사용 후 반드시 닫아주세요.</li>
    <li>트랜잭션 관리에 주의하세요 (commit/rollback).</li>
    <li>대량의 데이터 처리 시에는 배치 처리(batch)를 고려하세요.</li>
</ul>''',
                    'order': 12,
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

