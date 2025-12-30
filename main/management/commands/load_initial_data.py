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
        topics_data = {
            'network': [
                {
                    'title': '개요 및 큰 그림',
                    'slug': 'network-overview',
                    'content': '''<h2>개요 및 큰 그림</h2>
<p>네트워크는 데이터를 서로 전달하는 <strong>길</strong>과 이를 관리하는 <strong>규칙</strong>의 집합입니다. 여기서 길은 <em>라우팅(Routing)</em>과 <em>스위칭(Switching)</em>으로 나뉘고, 규칙은 <em>프로토콜(Protocol)</em>과 <em>보안 정책</em>으로 볼 수 있습니다.</p>
<div class="diagram">
<pre>
[PC/서버] → [스위치(L2)] → [라우터(L3)] → [방화벽/ACL] → [NAT] → [인터넷]
</pre>
</div>
<p>이 흐름을 이해하면, 네트워크가 어디에서 멈췄는지 빠르게 찾을 수 있습니다.</p>''',
                    'order': 1,
                },
                {
                    'title': '기본 용어와 개념',
                    'slug': 'network-concepts',
                    'content': '''<h2>기본 용어와 개념</h2>
<h3>핵심 용어 표</h3>
<table>
<thead>
<tr>
<th>쉬운 말</th>
<th>전문 용어</th>
<th>설명</th>
<th>현업 예시</th>
</tr>
</thead>
<tbody>
<tr>
<td>동네</td>
<td>Subnet</td>
<td>같은 네트워크 범위(같은 서브넷이면 L2에서 바로 연결)</td>
<td>사무실에서 192.168.10.0/24 대역</td>
</tr>
<tr>
<td>주소</td>
<td>IP</td>
<td>인터넷에서 목적지를 가리키는 숫자</td>
<td>공인 IP 203.0.113.10</td>
</tr>
<tr>
<td>이름표</td>
<td>MAC Address</td>
<td>L2에서 장비를 구분하는 식별자</td>
<td>스위치가 프레임 전달시 참고</td>
</tr>
<tr>
<td>규칙표</td>
<td>ACL</td>
<td>허용/차단 규칙의 목록</td>
<td>방화벽, 클라우드 Security Group</td>
</tr>
<tr>
<td>전화번호부</td>
<td>DNS</td>
<td>이름을 IP로 변환</td>
<td>example.com → 203.0.113.10</td>
</tr>
<tr>
<td>자동주소</td>
<td>DHCP</td>
<td>IP/게이트웨이/DNS를 자동 배정</td>
<td>사무실 PC IP 자동 할당</td>
</tr>
</tbody>
</table>
<h3>용어 설명</h3>
<p><strong>IP 주소</strong>는 컴퓨터의 주소를 나타냅니다. 집으로 비유하면, 집(호스트)과 동네(네트워크)를 구분하는 동·호수입니다.<br>
<strong>MAC 주소</strong>는 같은 네트워크 안에서 장비를 찾을 때 사용합니다. L2 스위칭이 이를 사용해 프레임을 전달합니다.<br>
<strong>포트(Port)</strong>는 같은 IP 내에서 어떤 서비스인지를 구분하는 창구입니다. 예를 들어, HTTP는 80번, HTTPS는 443번 포트를 사용합니다.</p>''',
                    'order': 2,
                },
                {
                    'title': '토폴로지와 설계',
                    'slug': 'network-topology',
                    'content': '''<h2>토폴로지와 설계</h2>
<p>네트워크 토폴로지는 장비를 어떻게 연결할지를 결정하는 설계 구조입니다. 설계가 잘못되면 장애가 빠르게 확산될 수 있습니다.</p>
<h3>대표 토폴로지 비교</h3>
<table>
<thead>
<tr>
<th>형태</th>
<th>장점</th>
<th>단점</th>
<th>적합한 환경</th>
<th>예시</th>
</tr>
</thead>
<tbody>
<tr>
<td>스타형</td>
<td>관리 편리</td>
<td>중앙 허브 장애 시 전체 영향</td>
<td>소규모 사무실</td>
<td>PC들이 한 스위치에 모두 연결</td>
</tr>
<tr>
<td>트리형</td>
<td>확장성 좋음</td>
<td>상위 장애 영향 큼</td>
<td>대규모 조직</td>
<td>코어 스위치 → 분배 → 접속</td>
</tr>
<tr>
<td>메시형</td>
<td>이중화 강력</td>
<td>설치 비용과 복잡도</td>
<td>중요 백본 네트워크</td>
<td>멀티벤더 스위치 간 백업 링크</td>
</tr>
<tr>
<td>하이브리드</td>
<td>유연한 설계</td>
<td>설계가 중요</td>
<td>현실 대부분</td>
<td>스타 + 메시</td>
</tr>
</tbody>
</table>
<h3>디자인 팁</h3>
<div class="callout">
<p>토폴로지 설계 시 다음을 고려하세요:</p>
<ul>
<li>중앙 장비의 고가용성(H/A) – 이중화 설계</li>
<li>장애 시 우회 경로 – STP 설정 및 트래픽 분산</li>
<li>확장성 – 사무실 확장시 트리형 구조가 유리</li>
</ul>
</div>''',
                    'order': 3,
                },
                {
                    'title': 'IP 주소와 서브넷',
                    'slug': 'network-ip-subnet',
                    'content': '''<h2>IP 주소와 서브넷</h2>
<p>네트워크 주소와 호스트 주소를 구분하는 법을 배우면, 라우팅과 접근제어의 기본을 이해할 수 있습니다.</p>
<h3>동네(서브넷) 계산</h3>
<p>서브넷이란 같은 네트워크에 속하는 IP 주소의 범위입니다. CIDR 표기에서 <code>/24</code>처럼 슬래시 뒤 숫자가 작을수록 대역이 크고, 숫자가 클수록 대역이 작습니다.</p>
<div class="example">
<strong>예:</strong> 192.168.10.0/24<br>
<ul>
<li>네트워크 주소: 192.168.10.0</li>
<li>브로드캐스트: 192.168.10.255</li>
<li>할당 가능한 주소: 192.168.10.1 ~ 192.168.10.254</li>
</ul>
</div>
<h3>VLSM과 슈퍼네팅</h3>
<p><strong>VLSM</strong>은 필요한 크기만큼 서브넷을 다양한 크기로 나눌 수 있게 합니다.<br>
<strong>슈퍼네팅</strong>은 여러 작은 서브넷을 묶어 하나의 큰 대역으로 표현합니다. 라우팅 테이블을 단순화할 때 사용합니다.</p>
<div class="example">
<strong>현업 예시:</strong> 지사별로 각기 다른 서브넷을 배정해야 할 때, 인원수가 적은 지사에 /28, 큰 지사에 /23 등을 할당합니다.
</div>''',
                    'order': 4,
                },
                {
                    'title': 'L2/L3 동작 원리',
                    'slug': 'network-l2-l3',
                    'content': '''<h2>L2/L3 동작 원리</h2>
<h3>L2: Ethernet과 MAC</h3>
<p>스위치는 L2 영역에서 MAC 주소를 기반으로 프레임을 전송합니다. ARP(Address Resolution Protocol)를 이용해 IP→MAC을 확인합니다.</p>
<h3>L3: IP와 라우팅</h3>
<p>라우터는 L3에서 IP 주소를 기반으로 패킷을 전달합니다. 라우팅 테이블을 참고하여 목적지에 맞는 다음 홉을 결정합니다.</p>
<div class="diagram">
<pre>
[L2] 192.168.10.5 (MAC: aa:bb) ↔ [스위치] ↔ 192.168.10.10 (MAC: cc:dd)
 ↳ 같은 서브넷이면 L2에서 직접 전달
[L3] 192.168.10.5 → 10.0.0.20
 ↳ 다른 서브넷이면 라우터를 경유 (게이트웨이)
</pre>
</div>''',
                    'order': 5,
                },
                {
                    'title': '스위칭과 VLAN',
                    'slug': 'network-switching-vlan',
                    'content': '''<h2>스위칭과 VLAN</h2>
<h3>MAC 학습과 포워딩</h3>
<p>스위치는 프레임이 들어오면 출발지 MAC을 CAM 테이블에 기록하고, 목적지 MAC을 알아두었다면 해당 포트로만 보냅니다.</p>
<h3>VLAN</h3>
<p>VLAN은 스위치 내에서 브로드캐스트 영역을 나누어 서로 다른 구역처럼 동작하게 합니다.</p>
<div class="example">
<strong>예:</strong> 인사부는 VLAN 10, 개발부는 VLAN 20으로 나누어 브로드캐스트가 교차되지 않도록 설계할 수 있습니다.
</div>
<h3>Trunk, Native VLAN</h3>
<p>Trunk는 여러 VLAN을 한 포트로 통과시키며, 프레임에 VLAN 번호를 태깅(802.1Q)합니다. Native VLAN은 태그 없이 전달되는 VLAN으로, 설정이 다르면 프레임이 섞일 수 있습니다.</p>''',
                    'order': 6,
                },
                {
                    'title': '라우팅과 경로 제어',
                    'slug': 'network-routing',
                    'content': '''<h2>라우팅과 경로 제어</h2>
<h3>정적 라우팅과 동적 라우팅</h3>
<p>정적 라우팅은 관리자가 직접 경로를 지정하고, 동적 라우팅은 라우터끼리 정보(OSPF, BGP 등)를 교환하여 자동으로 경로를 설정합니다.</p>
<h3>기본 경로(Default Route)</h3>
<p>모든 알 수 없는 경로는 기본 경로로 보내라는 규칙입니다. 예를 들어 "인터넷으로 나가는 모든 패킷은 203.0.113.1로 보내라"와 같이 설정합니다.</p>
<h3>최장 일치 원칙</h3>
<p>라우터는 여러 경로가 일치할 때, 가장 상세한(프리픽스가 긴) 경로를 우선합니다.</p>
<div class="example">
<strong>예:</strong> 192.168.0.0/16과 192.168.1.0/24가 동시에 존재하면, 192.168.1.100은 /24가 일치하므로 해당 경로로 갑니다.
</div>''',
                    'order': 7,
                },
                {
                    'title': '네트워크 핵심 서비스',
                    'slug': 'network-services',
                    'content': '''<h2>네트워크 핵심 서비스</h2>
<h3>DNS</h3>
<p>DNS는 도메인 이름을 IP 주소로 변환해 줍니다. 인터넷 이용 시 사용자가 기억하기 쉬운 이름을 사용할 수 있게 해 줍니다.</p>
<h3>DHCP</h3>
<p>DHCP는 네트워크 장치에 IP, 게이트웨이, DNS를 자동으로 할당합니다. 관리자가 수동으로 설정할 필요가 없어 편리합니다.</p>
<h3>NTP</h3>
<p>네트워크 장치 간 시간 동기화를 위해 NTP 서버를 사용합니다. 시간이 정확해야 로그 분석이나 인증서 검증에 문제가 생기지 않습니다.</p>''',
                    'order': 8,
                },
                {
                    'title': '보안, ACL, NAT',
                    'slug': 'network-security',
                    'content': '''<h2>보안, ACL, NAT</h2>
<h3>ACL(Access Control List)</h3>
<p>ACL은 네트워크 접근을 허용하거나 차단하는 규칙 집합입니다. 순서대로 처리되고, 일치하는 규칙이 있으면 이후 규칙은 평가하지 않습니다. 마지막에는 보통 암묵적인 거부가 존재합니다.</p>
<h3>NAT</h3>
<p>NAT(Network Address Translation)은 사설 IP를 공인 IP로 변환하는 기술입니다. 공유기에 연결된 여러 장치들이 하나의 공인 IP로 인터넷을 사용할 때 사용됩니다.</p>
<h3>보안 그룹과 NACL</h3>
<p>AWS 등 클라우드에서 보안 그룹(Security Group)은 인스턴스 단위, NACL(Network ACL)은 서브넷 단위로 적용되는 접근 제어입니다.</p>''',
                    'order': 9,
                },
                {
                    'title': '무선(Wi-Fi)과 클라우드 네트워킹',
                    'slug': 'network-wifi-cloud',
                    'content': '''<h2>무선(Wi-Fi)과 클라우드 네트워킹</h2>
<h3>무선 네트워크의 환경 요인</h3>
<p>무선 네트워크는 2.4GHz와 5GHz 대역을 주로 사용합니다. 2.4GHz는 도달 범위가 길지만 간섭이 많고, 5GHz는 빠르지만 도달 범위가 짧습니다. 채널을 잘 선택해야 간섭을 줄일 수 있습니다.</p>
<h3>클라우드(VPC, Subnet) 매핑</h3>
<p>클라우드에서는 VPC를 사설망으로 보고, 서브넷으로 구역을 나눕니다. 인터넷 출입을 위해 Internet Gateway(IGW)를, 프라이빗 구역에서 외부로만 나가기 위해 NAT Gateway를 사용합니다.</p>''',
                    'order': 10,
                },
                {
                    'title': '운영과 트러블슈팅',
                    'slug': 'network-troubleshooting',
                    'content': '''<h2>운영과 트러블슈팅</h2>
<h3>기본 진단 도구</h3>
<ul>
<li><strong>ping</strong>: 네트워크 연결 확인</li>
<li><strong>traceroute</strong>: 경로 추적</li>
<li><strong>nslookup / dig</strong>: DNS 문제 확인</li>
<li><strong>curl / netcat</strong>: 특정 포트 연결 테스트</li>
</ul>
<h3>문제 해결 순서</h3>
<ol>
<li>네트워크 환경(물리/무선) 확인</li>
<li>내 IP, 서브넷, 게이트웨이 확인</li>
<li>라우팅 테이블과 DNS 확인</li>
<li>포트와 ACL/방화벽 확인</li>
<li>NAT 설정, 클라우드 보안 그룹 확인</li>
</ol>
<h3>현업 사례</h3>
<div class="example">
<strong>예:</strong> VPN 접속 시, 특정 사이트만 열리지 않는다면?
<ul>
<li>VPN 경로가 강제되어 DNS 서버가 다르게 설정될 수 있음</li>
<li>VPN 터널이 MTU를 낮춰 단편화 문제가 발생할 수 있음</li>
<li>직원용 ACL에서 해당 포트가 차단될 수 있음</li>
</ul>
</div>''',
                    'order': 11,
                },
            ],
            'linux': [
                {
                    'title': '리눅스 설치',
                    'slug': 'linux-installation',
                    'content': '''<h2>1. 리눅스 설치</h2>

<p>
1. <a href="https://ubuntu.com/download/desktop" target="_blank">
  Ubuntu Desktop ISO 다운로드
</a>
</p>

<img src="/static/img/설치-1.png" width="800" alt="Ubuntu ISO 다운로드 화면">
<p>2. 설치 과정 </p>
<p>기본적으로 계속 next하면 된다</p>
<img src="/static/img/설치-2.png" width="800">
<img src="/static/img/설치-3.png" width="800">
<p>교육/실습은 1프로세서/2코어로 지정. 만약 서버용은 1프로세서/4코어 </p>
<img src="/static/img/설치-4.png" width="800">
<p>4096MB로 설정. 2048MB로 설정할 경우 우분투 설치 마지막에 프리징이 있을 수 있음. </p>
<img src="/static/img/설치-5.png" width="800">
<p>가상 머신 설치 후 해당 머신 마우스 우클릭 후 setting 클릭</p>
<img src="/static/img/설치-6.png" width="800">
<p>다운 받은 리눅스 ISO파일 설정 후 connect at power on 설정 클릭</p>
<img src="/static/img/설치-7.png" width="800">
<p>Enter 후 계속 next하면 된다</p>
<img src="/static/img/설치-8.png" width="800">
<p>원하는 언어 선택</p>
<img src="/static/img/설치-9.png" width="800">
<p>사용 계정 생성</p>
<img src="/static/img/설치-10.png" width="800">
<p>Enter 후 계속 next해가면 설치는 끝.</p>''',
                    'order': 1,
                },
                {
                    'title': '편의 및 필수 툴',
                    'slug': 'linux-tools',
                    'content': '''<h3>1) Hostname 수정</h3>
<p>
  기본 hostname이 길어 터미널 사용 시 가독성이 떨어지므로,
  식별이 쉬운 이름으로 변경한다.
</p>

<img src="/static/img/편의-1.png" width="800">

<pre><code>sudo hostnamectl set-hostname server1</code></pre>

<img src="/static/img/편의-2.png" width="800">

<hr>

<h3>2) 한글 입력기 설치</h3>
<p>
  Ubuntu 기본 설치 환경에서는 한글 입력이 불가능하므로
  IBus 기반 한글 입력기를 설치한다.
</p>

<h4>① 시스템 업데이트</h4>
<pre><code>sudo apt update && sudo apt upgrade -y</code></pre>

<h4>② IBus 및 한글 입력기 설치</h4>
<pre><code>sudo apt install -y ibus ibus-hangul</code></pre>

<h4>③ 입력기 프레임워크 설정</h4>
<pre><code>im-config -n ibus</code></pre>

<p>설정 후 재부팅</p>

<h4>④ 한글 입력 소스 추가</h4>
<p>
Settings → Keyboard → Add Input Source에서  
Korean(Hangul)을 추가한다.
</p>

<img src="/static/img/한글-4.png" width="800">

<h4>⑤ 입력 전환 키 설정</h4>
<p>
터미널에서 <code>ibus-setup</code> 실행 후  
Preferences → Hangul Toggle Key를 <strong>Right Alt (Alt_R)</strong>로 설정한다.
</p>

<img src="/static/img/한글-5.png" width="800">
<img src="/static/img/한글-6.png" width="800">

<p><strong>※ 위 설정을 통해 터미널 및 브라우저에서 한글 입력이 가능해진다.</strong></p>

<h3>3) vim (기본 텍스트 에디터)</h3>
<p>
  vim은 리눅스 환경에서 널리 사용되는 텍스트 편집기
</p>

<pre><code>sudo apt install -y vim</code></pre>

<hr>

<h3>4) curl / wget (API 테스트 및 파일 다운로드)</h3>
<p>
  curl과 wget은 네트워크 통신 및 파일 다운로드에 사용되는 도구로,
  클라우드 환경 및 API 테스트 시 필수적이다.
</p>

<pre><code>sudo apt install -y curl wget</code></pre>

<ul>
  <li><strong>curl</strong> : HTTP 요청, REST API 테스트</li>
  <li><strong>wget</strong> : 파일 다운로드 전용</li>
</ul>

<hr>

<h3>5) net-tools + iproute2 (네트워크 확인)</h3>
<p>
  네트워크 인터페이스 및 IP 정보를 확인하기 위한 도구를 설치한다.
</p>

<pre><code>sudo apt install -y net-tools iproute2</code></pre>

<hr>

<h3>6) tree (디렉토리 구조 확인)</h3>
<p>
  tree 명령어는 디렉토리 구조를 계층적으로 출력
</p>

<pre><code>sudo apt install -y tree</code></pre>

<p><strong>※ 위 도구들은 실습 및 서버 운용을 위해 필수적으로 설치된다.</strong></p>''',
                    'order': 2,
                },
                {
                    'title': '기본 명령어',
                    'slug': 'linux-commands',
                    'content': '''<h3>1) 경로 </h3>
<p>
  리눅스를 운용하기 위해선 먼저 절대 경로와 상대 경로를 이해할 필요가 있다.
<br>절대 경로는 /(루트 디렉토리)를 기준으로 하지만 상대 경로는 현재 위치를 기준으로 한다.
<br>보통 절대 경로를 사용하지만 실행 파일을 실행하려고 할 때 반드시 상대 경로를 사용한다.

</p>
<h3>2) cd (디렉토리 이동)</h3>

<p>
cd 명령어는 현재 작업 중인 디렉토리에서 다른 디렉토리로 이동할 때 사용한다.
</p>

<pre><code>예)cd ~/a/b/c</code></pre>
<img src="/static/img/cd-1.png" width="800">

<pre><code>예)cd ../ 현재 위치에서 상위 디렉토리로 이동</code></pre>
<img src="/static/img/cd-2.png" width="800">
<pre><code>예)cd ~ 홈 디렉토리로 이동</code></pre>
<pre><code>예)cd / 루트 디렉토리로 이동</code></pre>
<h3>3) pwd (현재 위치 확인)</h3>
<img src="/static/img/pwd.png" width="800">
<hr>

<h3>4) ls (디렉터리 목록 표시) </h3>
<pre><code>ls (목록만 표시)</code></pre>
<img src="/static/img/ls-1.png" width="800">
<pre><code>ls -l (권한,소유자,크기 등 상세하게)</code></pre>
<img src="/static/img/ls-2.png" width="800">
<pre><code>ls -la (l 속성에 더해서 숨김 파일까지 표시)</code></pre>
<img src="/static/img/ls-3.png" width="800">
<hr>

<h3>5) mkidr (디렉터리 생성) & rm (디렉터리 및 파일 삭제)</h3>
<pre><code>mkdir </code></pre>
<img src="/static/img/mkdir-1.png" width="800">
<pre><code>mkdir -p (상위 디렉터리까지 한번에 생성)</code></pre>
<img src="/static/img/mkdir-2.png" width="800">

<pre><code>rm -r (r 옵션은 하위 디렉터리까지 한번에 삭제)</code></pre>
<img src="/static/img/rm.png" width="800">
<pre><code>rm -rf 무조건 삭제</code></pre>
<pre><code>rm -ri 삭제 전 물어봄(추천)</code></pre>

<h3>6) 파일 생성 & 복사 & 이동 </h3>
<pre><code>touch (빈 파일 생성)</code></pre>
<img src="/static/img/touch.png" width="800">
<pre><code>cat & echo (파일 생성 및 내용 입력)</code></pre>
<img src="/static/img/e&c.png" width="800">
<pre><code>echo는 문자열을 출력하고, cat은 파일 내용을 출력하는 것이 기본 기능이다.</code></pre>
<pre><code>파일 생성이나 내용 입력은 리다이렉션(>, >>)을 사용한 응용 방식이다.
두 명령어 모두 '>' 사용 시 덮어쓰고, '>>' 사용 시 기존 내용 뒤에 추가한다.</code></pre>
<pre><code>보통 한 줄 입력은 echo, 여러 줄 입력은 cat을 사용한다.</code></pre>

<pre><code>cp (파일 및 디렉터리 복사)</code></pre>
<img src="/static/img/cp.png" width="800">
<pre><code>test.txt 파일을 a.txt로 복사한다.(원본은 유지된다.)
test.txt 파일을 myp2 디렉터리로 복사한다.
디렉터리 myp2를 myp3로 복사한다.(디렉터리 복사에는 -r 옵션 사용)</code></pre>

<pre><code>mv (파일 이동 및 이름 변경)</code></pre>
<img src="/static/img/mv.png" width="800">
<pre><code>a.txt 파일을 b.txt라고 파일명을 변경한다.
b.txt 파일을 myp2 디렉터리로 옮긴다.
디렉터리 myp3를 myp3-3로 디렉터리명을 변경한다.</code></pre>

<h3>7) 권한 </h3>
<pre><code>리눅스에서는 파일과 디렉터리에 대해 읽기(r), 쓰기(w), 실행(x) 권한을 관리한다.</code></pre>
<pre><code>권한의 대상은 소유자(user), 그룹(group), 기타 사용자(other)로 나뉜다.</code></pre>
<img src="/static/img/chmod-1.png" width="800">
<pre><code>chmod (권한 부여)</code></pre>
<pre><code>권한 부여 방식은 숫자 방식과 심볼 방식 2가지로 나뉜다.</code></pre>
<pre><code>숫자 방식이 자주 쓰이며 의미는 다음과 같다.</code></pre>
<pre><code>chmod [유저][그룹][그외]. r=4 w=2 x=1.</code></pre>
<img src="/static/img/chmod-2.png" width="800">
<pre><code>소유자는 rwx(4+2+1=7)권한을 가지고 그룹과 다른 이용자들은 rx(4+1=5) 권한만 있다</code></pre>
<pre><code>실행 파일이 아니어도 x권한을 부여할 수 있다.</code></pre>

<hr>
<pre><code>심볼 방식 의미는 다음과 같다.</code></pre>
<pre><code>chmod [대상][연산기호][권한]. 대상 (u g o).연산 (+ - =).권한 (r w x)</code></pre>
<img src="/static/img/chmod-3.png" width="800">
<pre><code>소유자의 권한만 rwx로 바뀌었다</code></pre>
<img src="/static/img/chmod-4.png" width="800">
<pre><code>소유자의 권한에서 w을 뺏다</code></pre>
<pre><code>"=" 연산은 기존의 권한을 빼고 지정 권한만 설정한다.</code></pre>
<pre><code># 꼭 알아둬야 할 것 #</code></pre>
<pre><code>디렉터리 권한에서 실행(x)은 해당 디렉터리에 접근할 수 있는 권한을 의미하며,
읽기(r) 권한이 있어도 실행(x) 권한이 없으면 내부 파일에 접근할 수 없다.
파일 삭제 권한은 파일 자체가 아니라 디렉터리의 쓰기(w)와 실행(x) 권한에 의해 결정된다.</code></pre>
<hr>

<h3>7) 프로세스 </h3>
<pre><code>프로세스란 실행 중인 프로그램이다.(예) code, sshd, ptyhon, vim 등등</code></pre>
<pre><code>ps</code></pre>
<img src="/static/img/ps-1.png" width="800">
<pre><code>현재 터미널에서 실행 중인 프로세스만 표시
(시스템 전체 프로세스는 아님)</code></pre>
<pre><code>ps aux</code></pre>
<img src="/static/img/ps-2.png" width="800">
<pre><code>시스템 전체 프로세스를 출력하므로 매우 많은 정보가 표시된다.
  모든 내용 이해할 필요 없음.</code></pre>
<pre><code>ps -eo pid,user,comm | grep 프로세스명 </code></pre>
<img src="/static/img/ps-3.png" width="800">
<pre><code>해당 프로세스의 pid,user,comm 만 출력</code></pre>
<pre><code>top </code></pre>
<img src="/static/img/top.png" width="800">
<pre><code>실시간 실행중인 프로세스들 목록. PID번호가 중요함.</code></pre>
<pre><code>kill PID번호</code></pre>
<img src="/static/img/top.png" width="800">
<pre><code>해당 프로세스 종료</code></pre>
<pre><code>만약 파이어폭스를 종료하고 싶으면 kill 4256을 입력하면 된다.</code></pre>

<pre><code>top의 정렬 순서는 실시간으로 cpu/메모리를 많이 사용하는 프로세스부터 나온다.
프로세스는 ps로 확인하고, top으로 관찰한 뒤, kill로 종료한다.</code></pre>

<h3>8) 서비스 관리 </h3>
<pre><code>서비스는 ps가 아니라 systemctl로 관리한다.</code></pre>
<pre><code>사용하는 systemctl의 명령어는 다음과 같다.</code></pre>
<pre><code>systemctl status 서비스명
systemctl start 서비스명
systemctl stop 서비스명
systemctl restart 서비스명
systemctl enable 서비스명
systemctl disable 서비스명
systemctl is-enabled 서비스명
</code></pre>
<pre><code>새로운 서비스를 시작할 경우의 실행할 명령어 순서는 
restart -> enable -> status로 상태 확인.</code></pre>
<img src="/static/img/status.png" width="800">
<pre><code>스크린샷 내용처럼 activate로 뜨면 정상 작동 중이다.</code></pre>
<pre><code>enable 명령어를 써줘야 재시작했을 때 자동으로 서비스가 시작된다.</code></pre>
<hr>

<h3>9) crontab </h3>
<pre><code>정해진 시간에 명령을 자동으로 실행하는 기능

crontab -l  등록된 작업 확인
crontab -e  작업 편집
crontab -r  작업 삭제</code></pre>

<pre><code>크론탭 설정은 * * * * * 이며, 왼쪽부터 분 시 일 월 요일을 뜻한다.
월은 1~12로, 1월부터 12월을 의미한다.
요일은 0 또는 7=일요일, 1=월요일 ~ 6=토요일이다.</code></pre>

<pre><code>숫자는 고정값을 의미하며, */N 형태는 N 간격 실행을 의미한다.</code></pre>

<pre><code>예를 들어 * * * * * 은 매분마다 실행된다.
예를 들어 */2 * * * * 은 2분마다 실행된다.</code></pre>

<img src="/static/img/crontab-1.png" width="800">
<pre><code>crontab -e 명령을 실행하면 편집기를 고르는 메뉴. 1번을 선택</code></pre>
<img src="/static/img/crontab-2.png" width="800">
<pre><code>맨 아랫줄에 */2 * * * * touch /home/tester/contrabtest.txt 추가</code></pre>
<pre><code>2분마다 contrabtest.txt 파일을 생성한다는 뜻</code></pre>
<pre><code>Ctrl + o(저장)후 엔터 그 다음 Ctrl + x(종료)</code></pre>
<img src="/static/img/crontab-3.png" width="800">
<pre><code>13:48에 파일 생성</code></pre>
<img src="/static/img/crontab-4.png" width="800">
<pre><code>13:50에 파일이 수정된걸 볼 수 있다</code></pre>''',
                    'order': 3,
                },
                {
                    'title': '서버',
                    'slug': 'linux-server',
                    'content': '''<h3>Linux 서버</h3>
<p>
리눅스는 무료 오픈소스이며, 높은 보안성과 안정성, 뛰어난 성능과 유연성을 제공해
서버 OS로 적합하다.
또한 재부팅 없는 업데이트, 효율적인 자원 관리, 빠른 버그 수정,
다양한 환경 지원, 클라우드·DevOps와의 높은 호환성이 큰 장점이다.

<p>
서버를 배우기 전에 포트의 개념을 알 필요가 있다.
</p>

<ul>
  <li>IP 주소: 어느 서버인가</li>
  <li>포트 번호: 그 서버 안에서 어떤 서비스인가</li>
  <li>프로세스: 그 포트를 실제로 열고 있는 프로그램</li>
</ul>

<p><strong>즉, 서버 = IP + 포트 + 프로세스</strong></p>

</p>

<h3>1) 웹 사이트 서버</h3>
<p>
사용자가 브라우저에 주소를 입력하면 그 요청을 받아서 응답을 보내줄 서버가 필요하다.
그 역할을 하는 것이 웹 서버다.
네트워크가 연결되고 IP 주소를 알아도 웹사이트 서버가 없으면
사용자는 요청을 보내도 응답을 받을 수 없다.
</p>

<p>Apache HTTP Server, Nginx, Lighttpd 등이 있다.</p>

<h4>Nginx 설치</h4>
<pre><code>sudo apt install -y nginx</code></pre>

<img src="/static/img/nginx-1.png" width="800">

<pre><code>systemctl enable nginx
systemctl restart nginx
systemctl status nginx</code></pre>

<p>
위 명령어를 차례대로 실행한 후
<code>active (running)</code> 상태를 확인한다.
</p>

<p>리눅스 파이어폭스 접속 후 주소창에 <code>localhost</code>를 입력한다.</p>
<img src="/static/img/nginx-2.png" width="800">

<p><strong>welcome to nginx!</strong>가 뜨면 정상이다.</p>

<h3>localhost</h3>
<p>
<code>localhost</code>는 현재 사용 중인 자기 자신의 컴퓨터를 가리키는 이름이다.
실제로는 IP 주소 <code>127.0.0.1</code>을 의미하며,
외부 네트워크를 거치지 않고 내 컴퓨터에서 실행 중인 서버를 확인할 때 사용한다.
</p>

<p>리눅스 터미널에서 <code>systemctl stop nginx</code>를 실행한다.</p>
<img src="/static/img/nginx-3.png" width="800">

<p>웹 서버를 꺼버리면 웹 페이지에 아무것도 표시되지 않는다.</p>

<p><code>sudo ss -tulpn | grep nginx</code></p>
<p>
<code>ss</code> 명령어는 현재 열려 있는 포트와 해당 포트를 사용하는 프로세스를 확인할 수 있다.
프로세스 정보는 관리자 권한이 필요하므로 <code>sudo</code>를 사용한다.
</p>

<img src="/static/img/nginx-4.png" width="800">
<p>포트 번호가 80번인걸 확인할 수 있다.</p>

<p>
지금까지 nginx를 통해 웹 서버가
<strong>프로세스로 실행되고, 포트를 열어 요청을 처리한다</strong>는 것을 확인했다.
이 구조는 다른 모든 서버에서도 동일하게 적용된다.
</p>

<hr>

<h3>2)DNS 서버</h3>
<p>
DNS는 이름을 IP 주소로 바꿔주는 서버다.

사람은 숫자(IP 주소)보다 이름을 쓰기 때문에
브라우저에서 도메인 이름을 입력하면,
DNS 서버가 해당 이름에 대응하는 IP 주소를 알려준다.
DNS가 없으면 IP 주소를 외워서 접속해야한다.

기본 포트는 <strong>53번</strong>이다.
</p>

<p><code>sudo apt install -y bind9</code></p>
<p><code>sudo systemctl status bind9</code></p>
<img src="/static/img/dns-1.png" width="800">
<p>active(running) 상태 확인.</p>
<pre><code>sudo systemctl enable bind9
sudo systemctl restart bind9
sudo systemctl status bind9</code></pre>

<p><code>sudo vim /etc/hosts</code></p>
<img src="/static/img/dns-2.png" width="800">
<p><code>127.0.0.1 linux-project.local 추가</code></p>
<img src="/static/img/dns-3.png" width="800">
<p><code>주소창을 보면 설정한 linux-project.local로 접속한걸 알 수 있다.</code></p>
<hr>

<h3>3) DHCP 서버</h3>

<p>
DHCP 서버는 클라이언트에게 IP 주소를 자동으로 할당해주는 서버이다.<br>
기본 포트는 <strong>67번(서버) / 68번(클라이언트)</strong>을 사용한다.
</p>

<p><code>sudo apt install isc-dhcp-server</code></p>
<p><code>sudo vim /etc/default/isc-dhcp-server</code></p>

<img src="/static/img/dhcp-1.png" width="800">
<p>
INTERFACESv4="ens33"로 수정한다. (DHCP 서버가 동작할 네트워크 인터페이스 지정)
</p>

<img src="/static/img/dhcp-2.png" width="800">
<p><code>ls /etc/netplan</code> 명령어로 설정 파일을 확인한다.</p>
<p><code>sudo vim /etc/netplan/01-network-manager-all.yaml</code></p>

<img src="/static/img/dhcp-3.png" width="800">
<p>
화면과 같이 수정하여 DHCP 서버에 고정 IP를 설정한다.
</p>
<p><code>sudo netplan apply</code> 명령어로 적용한다.</p>

<p>DHCP 설정 파일을 작성한다.</p>
<p><code>sudo vim /etc/dhcp/dhcpd.conf</code></p>

<img src="/static/img/dhcp-4.png" width="800">

<p>leases 파일을 생성한다.</p>
<p>
<code>
sudo touch /var/lib/dhcp/dhcpd.leases<br>
sudo chown root:root /var/lib/dhcp/dhcpd.leases<br>
sudo chmod 644 /var/lib/dhcp/dhcpd.leases
</code>
</p>

<p>설정 파일 문법을 최종 확인한다. (에러가 없어야 함)</p>
<p><code>sudo dhcpd -t -cf /etc/dhcp/dhcpd.conf</code></p>

<p>
<code>
sudo systemctl restart isc-dhcp-server<br>
sudo systemctl status isc-dhcp-server
</code>
</p>

<img src="/static/img/dhcp-5.png" width="800">

<p>
VMware 환경에서 DHCP 서버(server1)가 클라이언트(serverb)에 IP를 할당하는지 확인한다.
</p>

<p>server1(DHCP 서버)에서 로그 창을 실행한다.</p>
<p><code>sudo journalctl -u isc-dhcp-server -f</code></p>

<img src="/static/img/dhcp-6.png" width="800">
<p>DHCPREQUEST 192.168.238.130 로그를 확인한다.</p>

<p>serverb(클라이언트 서버)에서 최종 IP 할당 여부를 확인한다.</p>

<img src="/static/img/dhcp-7.png" width="800">
<p>IP 주소 192.168.238.130이 DHCP를 통해 할당된 것을 확인한다.</p>

<hr>

<h3>4) 데이터베이스(DB) 서버</h3>

<p>
데이터베이스 서버는 데이터를 체계적으로 저장하고 관리하기 위한 서버이다.
본 실습에서는 리눅스 환경에서 MariaDB를 설치하여
기본적인 데이터베이스 구성과 데이터 조작을 진행한다.
</p>

<p><code>sudo apt install -y mariadb-server</code></p>
<p><code>sudo systemctl status mariadb</code></p>
<img src="/static/img/db-1.png" width="800">

<p>서비스 상태가 <strong>Active: active (running)</strong> 인지 확인한다.</p>
<img src="/static/img/db-2.png" width="800">

<p>보안 설정 실행</p>
<p><code>sudo mysql_secure_installation</code></p>
<img src="/static/img/db-3.png" width="800">

<p>
처음 나오는 비밀번호 입력 질문은 Enter를 입력하고,
이후 질문은 모두 Y로 설정한다.
중간에 root 비밀번호 설정 단계에서만 비밀번호를 주의하여 입력한다.
</p>

<hr>

<p><strong>데이터베이스 생성</strong></p>
<p>
<pre><code>sudo mariadb
CREATE DATABASE testdb;
SHOW DATABASES;</code></pre>
</p>
<img src="/static/img/db-4.png" width="800">

<p>
SQL 명령어는 대문자로 작성하는 것이 관례이며,
각 명령어의 끝에는 반드시 세미콜론(;)을 붙인다.
</p>

<hr>

<p><strong>사용자 생성 및 권한 부여</strong></p>
<p>
<code>
CREATE USER 'testuser'@'localhost' IDENTIFIED BY '1234';
</code>
</p>

<p>
<pre><code>GRANT ALL PRIVILEGES ON testdb.* TO 'testuser'@'localhost';
FLUSH PRIVILEGES;</code></pre>
</p>

<p><code>mariadb -u testuser -p</code></p>
<img src="/static/img/db-5.png" width="800">

<p>
testuser 계정으로 접속 후
<code>USE testdb;</code> 명령 실행 시 에러가 발생하지 않으면
정상적으로 권한이 부여된 것이다.
</p>

<hr>

<p><strong>테이블 생성</strong></p>
<p>
contacts 테이블은 이름, 전화번호, 이메일 정보를 저장하기 위한 테이블이다.
각 컬럼의 의미는 다음과 같다.
</p>

<p>
<code>id</code> 컬럼은 각 데이터를 구분하기 위한 고유 식별자이며,
<code>INT</code> 타입으로 설정하였다.
<code>AUTO_INCREMENT</code> 옵션은 데이터가 추가될 때마다
값이 자동으로 증가하도록 하였다.
</p>

<p>
<code>PRIMARY KEY</code>는 테이블 내에서 중복될 수 없는 값이다.
</p>

<p>
<code>name VARCHAR(50)</code>는 이름을 저장하는 컬럼으로,
최대 50자의 문자열을 저장할 수 있다.
<code>NOT NULL</code> 옵션을 사용하여 반드시 값이 입력되도록 설정하였다.
</p>

<p>
<code>phone VARCHAR(20)</code>는 전화번호를 저장하는 컬럼이다.
전화번호에는 하이픈(-)이 포함될 수 있으므로
숫자형이 아닌 문자열 타입(VARCHAR)으로 설정하였다.
</p>

<p>
<code>email VARCHAR(100)</code>는 이메일 주소를 저장하는 컬럼이다.
</p>

<p>
VARCHAR는 가변 길이 문자열 타입으로,
실제 입력된 문자열 길이에 따라 저장 공간을 사용한다.
</p>

<p>
<pre><code>CREATE TABLE contacts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  phone VARCHAR(20),
  email VARCHAR(100)
);</code></pre>
</p>

<img src="/static/img/db-6.png" width="800">

<p><code>SHOW TABLES;</code></p>
<img src="/static/img/db-7.png" width="800">
<p>테이블 생성 확인</p>

<hr>

<p><strong>데이터 삽입</strong></p>
<p>
<pre><code>INSERT INTO contacts (name, phone, email) VALUES
('홍길동', '010-1111-2222', 'hong@test.com'),
('김철수', '010-3333-4444', 'kim@test.com'),
('이영희', '010-5555-6666', 'lee@test.com');</code></pre>
</p>

<p><strong>데이터 조회 (SELECT)</strong></p>
<p><code>SELECT * FROM contacts;</code></p>
<img src="/static/img/db-8.png" width="800">

<hr>

<p><strong>특정 데이터 조회</strong></p>

<p>이름으로 조회</p>
<p><code>SELECT * FROM contacts WHERE name = '김철수';</code></p>

<p>이메일로 조회</p>
<p><code>SELECT * FROM contacts WHERE email = 'lee@test.com';</code></p>

<p>전화번호 일부로 조회</p>
<p><code>SELECT * FROM contacts WHERE phone LIKE '010-5555%';</code></p>

<img src="/static/img/db-9.png" width="800">

<hr>

<p><strong>특정 데이터 삭제 (DELETE)</strong></p>

<p>
DELETE 명령어는 WHERE 조건 없이 실행할 경우
테이블의 모든 데이터가 삭제되므로 주의해야 한다.
</p>

<p>삭제 전 테이블 상태 확인</p>
<p><code>SELECT * FROM contacts;</code></p>

<p>이름으로 데이터 삭제</p>
<p><code>DELETE FROM contacts WHERE name = '김철수';</code></p>

<p>전화번호 일부로 데이터 삭제</p>
<p><code>DELETE FROM contacts WHERE phone LIKE '010-5555%';</code></p>

<p>삭제 결과 확인</p>
<p><code>SELECT * FROM contacts;</code></p>

<img src="/static/img/db-10.png" width="800">
''',
                    'order': 4,
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

