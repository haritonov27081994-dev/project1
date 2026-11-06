from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Post
from .forms import PostForm

def home_page_view(request):
    """Главная страница блога."""
    posts = Post.objects.filter(status="published").order_by('-created_at')[:5]
    return render(request, 'blog/pages/index.html', {'posts': posts})

def post_list_view(request):
    """Страница со списком всех постов."""
    posts = Post.objects.filter(status="published").order_by('-created_at')
    return render(request, 'blog/pages/post_list.html', {'posts': posts})

def post_detail_view(request, post_slug):
    """Страница детального просмотра одного поста по его слагу с защитой черновиков."""
    if request.user.is_authenticated:
        condition = Q(slug=post_slug) & (Q(status="published") | Q(author=request.user))
    else:
        condition = Q(slug=post_slug) & Q(status="published")
        
    post = get_object_or_404(Post, condition)
    return render(request, 'blog/pages/post_detail.html', {'post': post})

@login_required
def post_add_view(request):
    """Страница добавления нового поста."""
    form = PostForm(request.POST or None, request.FILES or None)
    
    if request.method == "POST":
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:post_detail', post_slug=post.slug)

    return render(
        request,
        'blog/pages/post_form.html',
        {
            "form": form,
            "title": "Добавить пост",
            "h1": "Новый пост",
            "submit_button_text": "Добавить",
        }
    )

@login_required
def post_edit_view(request, post_id):
    """Страница редактирования существующего поста по его ID."""
    post = get_object_or_404(Post, id=post_id)
    
    if request.user != post.author:
        return render(request, 'blog/pages/not_allowed.html')
        
    extra_context = {
        "title": "Редактировать пост",
        "h1": "Редактирование",
        "submit_button_text": "Сохранить",
    }

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect("blog:post_detail", post_slug=post.slug)
        return render(
            request,
            'blog/pages/post_form.html',
            context={
                "form": form,
                **extra_context,
            }
        )

    form = PostForm(instance=post)
    return render(
        request,
        'blog/pages/post_form.html',
        context={
            "form": form,
            **extra_context,
        }
    )

@login_required
def post_remove_view(request, post_id):
    """Страница удаления поста с подтверждением."""
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author:
        return render(request, 'blog/pages/not_allowed.html')

    if request.method == "POST":
        post.delete()
        return redirect("blog:post_list")

    return render(request, 'blog/pages/post_remove_confirm.html', {'post': post})
