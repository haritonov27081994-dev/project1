from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.home_page_view, name="home_page"),
    path('posts/', views.post_list_view, name="post_list"),
    path('posts/category/<slug:category_slug>/', views.category_posts_view, name="category_posts"),
    path('posts/tag/<slug:tag_slug>/', views.tag_posts_view, name="tag_posts"),
    path('posts/add/', views.post_add_view, name='post_add'),
    path('posts/<slug:post_slug>/', views.post_detail_view, name='post_detail'),
    path('posts/<int:post_id>/edit/', views.post_edit_view, name="post_edit"),
    path('posts/<int:post_id>/remove/', views.post_remove_view, name="post_remove"),
]
