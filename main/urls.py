from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('search/', views.search, name='search'),
    path('healthz/', views.healthz, name='healthz'),
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

