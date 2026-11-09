from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Post, Category, Tag
from .forms import PostForm

class HomePageView(ListView):
    """Главная страница блога (показывает 5 последних опубликованных постов)."""
    model = Post
    template_name = 'blog/pages/index.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return Post.objects.filter(status="published").order_by('-created_at')[:5]


class PostListView(ListView):
    """Страница со списком всех опубликованных постов с пагинацией из урока."""
    queryset = Post.objects.filter(status="published").order_by('-created_at')
    context_object_name = 'posts'
    template_name = 'blog/pages/post_list.html'
    paginate_by = 3  # Количество постов на одной странице


class CategoryPostsView(ListView):
    """Страница со списком постов конкретной категории с пагинацией."""
    context_object_name = 'posts'
    template_name = 'blog/pages/category_posts.html'
    paginate_by = 3

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        return self.category.posts.filter(status='published').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class TagPostsView(ListView):
    """Страница со списком постов с определенным тегом с пагинацией."""
    model = Post
    template_name = 'blog/pages/tag_posts.html'
    context_object_name = 'posts'
    paginate_by = 3

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['tag_slug'])
        return self.tag.posts.filter(status='published').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context


class PostDetailView(DetailView):
    """Страница детального просмотра одного поста по его слагу с защитой черновиков из урока."""
    model = Post
    slug_url_kwarg = 'post_slug'
    template_name = 'blog/pages/post_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Post.objects.filter(
                Q(status="published") | Q(author=self.request.user)
            )
        return Post.objects.filter(status="published")


class PostAddView(LoginRequiredMixin, CreateView):
    """Страница добавления нового поста из урока."""
    form_class = PostForm
    extra_context = {
        "title": "Добавить пост",
        "h1": "Новый пост",
        "submit_button_text": "Добавить"
    }
    template_name = 'blog/pages/post_form.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()

        tag_names = form.cleaned_data.get('tags_input', [])
        for tag_name in tag_names:
            tag, _ = Tag.objects.get_or_create(
                name__iexact=tag_name, 
                defaults={'name': tag_name}
            )
            post.tags.add(tag)

        return redirect('blog:post_detail', post_slug=post.slug)


class PostEditView(UpdateView):
    """Страница редактирования существующего поста по его ID."""
    model = Post
    pk_url_kwarg = 'post_id'
    form_class = PostForm
    template_name = 'blog/pages/post_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.user != self.object.author:
            return render(request, 'blog/pages/not_allowed.html')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Редактировать пост"
        context['h1'] = "Редактирование"
        context['submit_button_text'] = "Сохранить"
        context['form'].fields['tags_input'].initial = ", ".join(tag.name for tag in self.object.tags.all())
        return context

    def form_valid(self, form):
        form.save()
        self.object.tags.clear()
        tag_names = form.cleaned_data.get('tags_input', [])
        for tag_name in tag_names:
            tag, _ = Tag.objects.get_or_create(
                name__iexact=tag_name, 
                defaults={'name': tag_name}
            )
            self.object.tags.add(tag)
        return redirect('blog:post_detail', post_slug=self.object.slug)


class PostRemoveView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Страница удаления поста с подтверждением."""
    model = Post
    template_name = 'blog/pages/post_remove_confirm.html'
    pk_url_kwarg = 'post_id'
    success_url = reverse_lazy('blog:post_list')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
