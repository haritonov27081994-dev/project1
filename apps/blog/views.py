from django.shortcuts import get_object_or_404, redirect, render
from .models import Post
from .forms import PostForm


def home_page_view(request):
    return render(request, template_name='blog/pages/index.html')


def post_list_view(request):
    posts = Post.objects.all()
    return render(request, template_name='blog/pages/post_list.html', context={'posts': posts})


def post_detail_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'blog/pages/post_detail.html', {'post': post})


def post_add_view(request):
    form = PostForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            post = form.save()  # Автоматически сохраняет пост в БД и возвращает созданный объект
            return redirect('blog:post_detail', post_id=post.id)

    return render(request, 'blog/pages/post_add.html', {"form": form})
