from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post
from .forms import PostForm
from django.views.decorators.http import require_POST

def home_page_view(request):
    """Главная страница блога."""
    posts = Post.objects.all().order_by('-created_at')[:5]
    return render(request, 'blog/pages/index.html', {'posts': posts})

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
    return render(request, 'blog/pages/post_form.html', {'form': form})

@login_required
def post_edit_view(request, post_id):
    """Страница редактирования существующего поста."""
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None, instance=post)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post.id)
    return render(request, 'blog/pages/post_form.html', {'form': form, 'post': post})

@require_POST
def post_remove_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.delete()
    return redirect('blog:post_list')