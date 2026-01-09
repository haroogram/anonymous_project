// 메인 JavaScript 파일

document.addEventListener('DOMContentLoaded', function() {
    // 모바일 메뉴 토글
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mainNav = document.getElementById('main-nav');
    
    if (mobileMenuToggle && mainNav) {
        mobileMenuToggle.addEventListener('click', function() {
            this.classList.toggle('active');
            mainNav.classList.toggle('active');
        });

        // 메뉴 링크 클릭 시 모바일 메뉴 닫기
        const navLinks = mainNav.querySelectorAll('a');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                mobileMenuToggle.classList.remove('active');
                mainNav.classList.remove('active');
            });
        });

        // 화면 크기 변경 시 메뉴 상태 초기화
        let resizeTimer;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(function() {
                if (window.innerWidth > 768) {
                    mobileMenuToggle.classList.remove('active');
                    mainNav.classList.remove('active');
                }
            }, 250);
        });
    }

    // 스크롤 시 헤더 스타일 변경
    const header = document.querySelector('.header');
    let lastScroll = 0;

    window.addEventListener('scroll', function() {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll > 100) {
            header.style.boxShadow = '0 4px 8px rgba(0,0,0,0.15)';
        } else {
            header.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
        }
        
        lastScroll = currentScroll;
    });

    // 부드러운 스크롤
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href.length > 1) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    // 헤더 높이를 고려한 추가 오프셋 계산
                    const header = document.querySelector('.header');
                    const headerHeight = header ? header.offsetHeight : 0;
                    const offset = headerHeight + 40; // 헤더 높이 + 추가 여유 공간
                    
                    const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - offset;
                    
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // 카드 호버 효과 강화
    const cards = document.querySelectorAll('.category-card, .topic-card, .feature-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transition = 'all 0.3s ease';
        });
    });

    // 방문자 통계 동적 로드
    (function loadVisitorStats() {
        const todayEl = document.getElementById('today-visitors');
        const totalEl = document.getElementById('total-visitors');
        if (!todayEl || !totalEl) {
            return;
        }

        fetch('/api/visitors/stats/')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // API 스펙: views.visitor_stats에서 today, today_unique, total 반환
                const today = data.today_unique ?? data.today ?? 0;
                const total = data.total ?? 0;
                todayEl.textContent = today;
                totalEl.textContent = total;
            })
            .catch(error => {
                console.error('방문자 통계 로드 실패:', error);
            });
    })();
});

