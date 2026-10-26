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
            post = form.save()
            return redirect('blog:post_detail', post_id=post.id)

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


def post_edit_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    extra_context = {
        "title": "Редактировать пост",
        "h1": "Редактирование",
        "submit_button_text": "Сохранить",
    }

    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect("blog:post_detail", post_id=post.id)
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
