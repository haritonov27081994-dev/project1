from django.shortcuts import get_object_or_404, redirect, render
from blog.models import Post


def home_page_view(request):
    return render(request, template_name='blog/pages/index.html')


def post_list_view(request):
    posts = Post.objects.all()
    return render(request, template_name='blog/pages/post_list.html', context={'posts': posts})


def post_detail_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'blog/pages/post_detail.html', {'post': post})


def post_add_view(request):
    # 1. Если данные отправлены методом POST, обрабатываем их
    if request.method == "POST":
        title = request.POST['title'].strip()
        text = request.POST['text'].strip()
        
        errors = {}
        if not title:
            errors['title'] = 'Заголовок поста обязателен к заполнению.'
        if not text:
            errors['text'] = 'Текст поста обязателен к заполнению.'
            
        if errors:
            context = {
                'errors': errors,
                'title': title,
                'text': text
            }
            return render(request, 'blog/pages/post_add.html', context)
            
        post = Post.objects.create(title=title, text=text)
        return redirect('blog:post_detail', post_id=post.id)
        
    # 2. Если это обычный переход на страницу (GET), просто отдаем пустую форму
    return render(request, 'blog/pages/post_add.html')