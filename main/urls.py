from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:category>/', views.tutorial, name='tutorial'),
    path('<str:category>/<str:topic>/', views.topic_detail, name='topic_detail'),
    # 접속자 수 통계 API
    path('api/visitors/stats/', views.visitor_stats, name='visitor_stats'),
    path('api/visitors/detail/', views.visitor_stats_detail, name='visitor_stats_detail'),
]

