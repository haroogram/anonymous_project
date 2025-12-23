from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:category>/', views.tutorial, name='tutorial'),
    path('<str:category>/<str:topic>/', views.topic_detail, name='topic_detail'),
]

