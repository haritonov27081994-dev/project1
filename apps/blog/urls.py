from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.home_page_view, name="home_page"),
    path('posts/', views.post_list_view, name="post_list"),
    path('posts/<int:post_id>/', views.post_detail_view, name='post_detail'),# Добавить эту строку
]