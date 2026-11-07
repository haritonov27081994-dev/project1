from django.shortcuts import redirect
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
    """Страница со списком всех опубликованных постов (в стиле урока через queryset)."""
    queryset = Post.objects.filter(status="published").order_by('-created_at')
    context_object_name = 'posts'
    template_name = 'blog/pages/post_list.html'


class CategoryPostsView(ListView):
    """Страница со списком постов конкретной категории."""
    model = Post
    template_name = 'blog/pages/category_posts.html'
    context_object_name = 'posts'

    def get_queryset(self):
        self.category = Category.objects.get(slug=self.kwargs['category_slug'])
        return self.category.posts.filter(status='published').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class TagPostsView(ListView):
    """Страница со списком постов с определенным тегом."""
    model = Post
    template_name = 'blog/pages/tag_posts.html'
    context_object_name = 'posts'

    def get_queryset(self):
        self.tag = Tag.objects.get(slug=self.kwargs['tag_slug'])
        return self.tag.posts.filter(status='published').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context


class PostDetailView(DetailView):
    """Страница детального просмотра одного поста по его слагу с защитой черновиков."""
    model = Post
    template_name = 'blog/pages/post_detail.html'
    context_object_name = 'post'
    slug_url_kwarg = 'post_slug'

    def get_object(self, queryset=None):
        if self.request.user.is_authenticated:
            condition = Q(slug=self.kwargs['post_slug']) & (Q(status="published") | Q(author=self.request.user))
        else:
            condition = Q(slug=self.kwargs['post_slug']) & Q(status="published")
        from django.shortcuts import get_object_or_404
        return get_object_or_404(Post, condition)


class PostCreateView(LoginRequiredMixin, CreateView):
    """Страница добавления нового поста с автоматической обработкой текстовых тегов."""
    model = Post
    form_class = PostForm
    template_name = 'blog/pages/post_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Добавить пост",
            "h1": "Новый пост",
            "submit_button_text": "Добавить",
        })
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        
        tag_names = form.cleaned_data.get('tags_input', [])
        for tag_name in tag_names:
            tag, _ = Tag.objects.get_or_create(
                name__iexact=tag_name, 
                defaults={'name': tag_name}
            )
            self.object.tags.add(tag)
            
        return response


class PostEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Страница редактирования существующего поста по его ID."""
    model = Post
    form_class = PostForm
    template_name = 'blog/pages/post_form.html'
    pk_url_kwarg = 'post_id'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Редактировать пост",
            "h1": "Редактирование",
            "submit_button_text": "Сохранить",
        })
        return context

    def get_initial(self):
        initial = super().get_initial()
        initial['tags_input'] = ", ".join(tag.name for tag in self.get_object().tags.all())
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        post = self.object
        
        post.tags.clear()
        tag_names = form.cleaned_data.get('tags_input', [])
        for tag_name in tag_names:
            tag, _ = Tag.objects.get_or_create(
                name__iexact=tag_name, 
                defaults={'name': tag_name}
            )
            post.tags.add(tag)
            
        return response


class PostRemoveView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Страница удаления поста с подтверждением."""
    model = Post
    template_name = 'blog/pages/post_remove_confirm.html'
    pk_url_kwarg = 'post_id'
    success_url = reverse_lazy('blog:post_list')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
