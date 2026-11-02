from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

# Используем абсолютный импорт через корень apps, настроенный в settings.py
from blog.models import Post
from blog.forms import PostForm

def home_page_view(request):
    """Главная страница блога."""
    posts = Post.objects.all().order_by('-created_at')[:5]
    return render(request, 'blog/pages/home.html', {'posts': posts})

def post_list_view(request):
    """Страница со списком всех постов."""
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'blog/pages/post_list.html', {'posts': posts})

def post_detail_view(request, post_id):
    """Страница детального просмотра одного поста."""
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'blog/pages/post_detail.html', {'post': post})

@login_required
def post_add_view(request):
    """Страница добавления нового поста."""
    form = PostForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:post_list')
    return render(request, 'blog/pages/post_add.html', {'form': form})

@login_required
def post_edit_view(request, post_id):
    """Страница редактирования существующего поста."""
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None, instance=post)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post.id)
    return render(request, 'blog/pages/post_edit.html', {'form': form, 'post': post})
