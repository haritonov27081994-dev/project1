from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.HomePageView.as_view(), name="home_page"),
    path('posts/', views.PostListView.as_view(), name="post_list"),
    path('posts/category/<slug:category_slug>/', views.CategoryPostsView.as_view(), name="category_posts"),
    path('posts/tag/<slug:tag_slug>/', views.TagPostsView.as_view(), name="tag_posts"),
    path('posts/add/', views.PostAddView.as_view(), name='post_add'),  # Исправлено на PostAddView
    path('posts/<slug:post_slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:post_id>/edit/', views.PostEditView.as_view(), name="post_edit"),
    path('posts/<int:post_id>/remove/', views.PostRemoveView.as_view(), name="post_remove"),
]
