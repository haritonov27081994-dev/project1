from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name="login"),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path("favorite-posts/", views.FavoritePostsView.as_view(), name="favorite_posts"),
    path("<str:username>/", views.ProfileView.as_view(), name='profile'),
]
