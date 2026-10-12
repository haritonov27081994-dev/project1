from django.shortcuts import get_object_or_404, redirect, render
from blog.models import Post


def home_page_view(request):
    return render(request, template_name='blog/index.html')


def post_list_view(request):
    posts = Post.objects.all()
    return render(request, template_name='blog/post_list.html', context={'posts': posts})


def post_detail_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'blog/post_detail.html', {'post': post})


def post_add_view(request):
    if request.method == "GET":
        return render(request, 'blog/post_add.html')
    elif request.method == "POST":
        post = Post.objects.create(
            title=request.POST['title'],
            text=request.POST['text']
        )
        return redirect('blog:post_detail', post_id=post.id)