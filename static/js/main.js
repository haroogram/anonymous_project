// 메인 JavaScript 파일

/** 고정(sticky) 헤더 + 여유 공간 — 앵커 스크롤 시 요소가 헤더에 가리지 않도록 */
function getHeaderAnchorOffset() {
    var header = document.querySelector('.header');
    var headerHeight = header ? header.offsetHeight : 0;
    return headerHeight + 40;
}

/**
 * URL 해시(#comments, #comment-12 등) 대상으로 스크롤 (헤더 높이만큼 위로 보정).
 * 전체 페이지 로드 후 브라우저 기본 앵커 이동을 덮어씀.
 */
function scrollToHashTargetWithHeaderOffset() {
    var hash = window.location.hash;
    if (!hash || hash.length < 2) {
        return;
    }
    var id;
    try {
        id = decodeURIComponent(hash.slice(1));
    } catch (e) {
        return;
    }
    if (!id) {
        return;
    }
    var target = document.getElementById(id);
    if (!target) {
        return;
    }
    var offset = getHeaderAnchorOffset();
    var top = target.getBoundingClientRect().top + window.pageYOffset - offset;
    window.scrollTo({
        top: Math.max(0, top),
        behavior: 'auto'
    });
    requestAnimationFrame(function () {
        highlightNotificationCommentFromHash();
    });
}

/** 알림 등으로 #comment-{id} 로 들어온 경우, 해당 댓글만 잠시 부드럽게 강조 */
function highlightNotificationCommentFromHash() {
    var hash = window.location.hash;
    if (!hash || hash.length < 2) {
        return;
    }
    var id;
    try {
        id = decodeURIComponent(hash.slice(1));
    } catch (e) {
        return;
    }
    if (!/^comment-\d+$/.test(id)) {
        return;
    }
    var el = document.getElementById(id);
    if (!el || !el.classList.contains('comment-item')) {
        return;
    }

    document.querySelectorAll('.comment-item--notif-target').forEach(function (n) {
        n.classList.remove('comment-item--notif-target');
    });

    el.classList.add('comment-item--notif-target');

    var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduced) {
        window.setTimeout(function () {
            el.classList.remove('comment-item--notif-target');
        }, 2800);
        return;
    }

    var onEnd = function (e) {
        if (e.animationName !== 'notifCommentHighlight') {
            return;
        }
        el.removeEventListener('animationend', onEnd);
        el.classList.remove('comment-item--notif-target');
    };
    el.addEventListener('animationend', onEnd);
}

document.addEventListener('DOMContentLoaded', function() {
    // Django 세션 메시지 + 미읽음 자유게시판 알림 → 오른쪽 토스트 (순서: 메시지 먼저, 알림 다음)
    (function initDjangoToasts() {
        const stack = document.getElementById('toast-stack');
        if (!stack) {
            return;
        }

        const holders = [];
        const sources = [];
        const msgHolder = document.getElementById('django-message-sources');
        const notifHolder = document.getElementById('board-notification-toast-sources');
        if (msgHolder) {
            holders.push(msgHolder);
            sources.push.apply(sources, Array.from(msgHolder.querySelectorAll('.toast-source')));
        }
        if (notifHolder) {
            holders.push(notifHolder);
            sources.push.apply(sources, Array.from(notifHolder.querySelectorAll('.toast-source')));
        }
        holders.forEach(function (h) {
            h.remove();
        });
        if (!sources.length) {
            return;
        }

        const LEVELS = ['debug', 'info', 'success', 'warning', 'error'];

        const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        sources.forEach(function (src, index) {
            const tagStr = src.dataset.tags || '';
            const tags = tagStr.split(/\s+/).filter(Boolean);
            const level = tags.find(function (t) {
                return LEVELS.indexOf(t) !== -1;
            }) || 'info';
            const text = src.textContent.trim();
            if (!text) {
                return;
            }

            const toast = document.createElement('div');
            toast.className = 'toast toast--' + level;
            toast.setAttribute('role', 'status');

            const span = document.createElement('span');
            span.className = 'toast__text';
            span.textContent = text;
            toast.appendChild(span);

            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'toast__close';
            btn.setAttribute('aria-label', '닫기');
            btn.innerHTML = '\u00d7';
            toast.appendChild(btn);

            stack.appendChild(toast);

            var hideTimer = null;

            function dismissToast() {
                if (toast.dataset.dismissing === '1') {
                    return;
                }
                toast.dataset.dismissing = '1';
                if (hideTimer) {
                    clearTimeout(hideTimer);
                    hideTimer = null;
                }
                toast.classList.remove('is-visible');
                if (reducedMotion) {
                    toast.remove();
                    return;
                }
                var onEnd = function (e) {
                    if (e.propertyName !== 'transform' && e.propertyName !== 'opacity') {
                        return;
                    }
                    toast.removeEventListener('transitionend', onEnd);
                    clearTimeout(fallbackRemove);
                    toast.remove();
                };
                var fallbackRemove = setTimeout(function () {
                    toast.removeEventListener('transitionend', onEnd);
                    if (toast.parentNode) {
                        toast.remove();
                    }
                }, 450);
                toast.addEventListener('transitionend', onEnd);
            }

            btn.addEventListener('click', dismissToast);

            if (reducedMotion) {
                toast.classList.add('is-visible');
            } else {
                requestAnimationFrame(function () {
                    requestAnimationFrame(function () {
                        toast.classList.add('is-visible');
                    });
                });
            }

            var delay = 4200 + index * 350;
            hideTimer = setTimeout(dismissToast, delay);
        });
    })();

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

    // 부드러운 스크롤 (같은 페이지 내 # 링크)
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href.length > 1) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    const offset = getHeaderAnchorOffset();
                    const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - offset;
                    window.scrollTo({
                        top: Math.max(0, targetPosition),
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // 알림·댓글 등 풀 리로드로 들어온 URL 해시: 브라우저 기본 스크롤을 헤더 보정으로 교체
    requestAnimationFrame(function () {
        requestAnimationFrame(scrollToHashTargetWithHeaderOffset);
    });

    window.addEventListener('hashchange', function () {
        scrollToHashTargetWithHeaderOffset();
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

