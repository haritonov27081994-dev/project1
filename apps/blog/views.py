from django.shortcuts import render
from django.http import HttpResponse
from .models import Post

# Главная страница
def home_page_view(request):
    return render(request, template_name='blog/index.html')

# Страница со списком всех постов
def post_list_view(request):
    posts = Post.objects.all()
    return render(request, template_name='blog/post_list.html', context={'posts': posts})