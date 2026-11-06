from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Post, Category, Tag
from .forms import PostForm

def home_page_view(request):
    """Главная страница блога."""
    posts = Post.objects.filter(status="published").order_by('-created_at')[:5]
    return render(request, 'blog/pages/index.html', {'posts': posts})

def post_list_view(request):
    """Страница со списком всех постов."""
    posts = Post.objects.filter(status="published").order_by('-created_at')
    return render(request, 'blog/pages/post_list.html', {'posts': posts})

def category_posts_view(request, category_slug):
    """Страница со списком опубликованных постов конкретной категории."""
    category = get_object_or_404(Category, slug=category_slug)
    posts = category.posts.filter(status='published').order_by('-created_at')
    context = {
        'category': category,
        'posts': posts
    }
    return render(request, 'blog/pages/category_posts.html', context)

def tag_posts_view(request, tag_slug):
    """Страница со списком опубликованных постов с определенным тегом."""
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = tag.posts.filter(status='published').order_by('-created_at')
    context = {
        'tag': tag,
        'posts': posts
    }
    return render(request, 'blog/pages/tag_posts.html', context)

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
    """Страница добавления нового поста с текстовым вводом тегов."""
    form = PostForm(request.POST or None, request.FILES or None)
    
    if request.method == "POST":
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            
            # Обработка и автоматическое создание текстовых тегов
            tag_names = form.cleaned_data.get('tags_input')
            for tag_name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                post.tags.add(tag)
                
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
    """Страница редактирования существующего поста с текстовым вводом тегов."""
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
            
            # Обновление текстовых тегов при редактировании
            post.tags.clear()
            tag_names = form.cleaned_data.get('tags_input')
            for tag_name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                post.tags.add(tag)
                
            return redirect("blog:post_detail", post_slug=post.slug)
        return render(
            request,
            'blog/pages/post_form.html',
            context={
                "form": form,
                **extra_context,
            }
        )

    # Передаем существующие теги поста строкой через запятую в форму
    existing_tags = ", ".join(tag.name for tag in post.tags.all())
    form = PostForm(instance=post, initial={'tags_input': existing_tags})
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
