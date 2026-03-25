from django.urls import path
from . import error_views, views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('search/', views.search, name='search'),
    path('healthz/', views.healthz, name='healthz'),
    # CloudFront/ALB 등에서 단순 라우팅 가능한 에러 페이지 엔드포인트
    path('errors/400/', lambda request: error_views.error_page(request, 400), name='error_400'),
    path('errors/403/', lambda request: error_views.error_page(request, 403), name='error_403'),
    path('errors/404/', lambda request: error_views.error_page(request, 404), name='error_404'),
    path('errors/413/', lambda request: error_views.error_page(request, 413), name='error_413'),
    path('errors/429/', lambda request: error_views.error_page(request, 429), name='error_429'),
    path('errors/500/', lambda request: error_views.error_page(request, 500), name='error_500'),
    # 자유게시판
    path('board/', views.board_list, name='board_list'),
    path('board/new/', views.board_create, name='board_create'),
    path('board/<int:pk>/', views.board_detail, name='board_detail'),
    path('board/<int:pk>/edit/', views.board_update, name='board_update'),
    path('board/<int:pk>/delete/', views.board_delete, name='board_delete'),
    path(
        'board/<int:post_pk>/attachment/<int:attachment_pk>/download/',
        views.board_attachment_download,
        name='board_attachment_download',
    ),
    # 인증 관련
    path('auth/signup/', views.signup, name='auth_signup'),
    path('auth/signup/complete/', views.signup_complete, name='auth_signup_complete'),
    path('auth/login/', views.login_view, name='auth_login'),
    path('auth/logout/', views.logout_view, name='auth_logout'),
    path('auth/activate/<uidb64>/<token>/', views.activate, name='auth_activate'),
    # 튜토리얼/콘텐츠
    path('<str:category>/', views.tutorial, name='tutorial'),
    path('<str:category>/<str:topic>/', views.topic_detail, name='topic_detail'),
    # 접속자 수 통계 API
    path('api/visitors/stats/', views.visitor_stats, name='visitor_stats'),
    path('api/visitors/detail/', views.visitor_stats_detail, name='visitor_stats_detail'),
]

