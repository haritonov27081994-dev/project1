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
    # Создаем форму один раз: если POST — с данными, если GET — пустую
    form = PostForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            post = Post.objects.create(
                title=form.cleaned_data['title'],
                text=form.cleaned_data['text']
            )
            return redirect('blog:post_detail', post_id=post.id)

    # Этот рендер сработает и для GET-запроса (отдаст пустую форму), 
    # и для POST-запроса, если форма не прошла валидацию (отдаст форму с ошибками)
    return render(request, 'blog/pages/post_add.html', {"form": form})
