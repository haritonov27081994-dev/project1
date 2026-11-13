from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import PostForm
from .models import Category, Post, Tag


class HomePageView(ListView):
    """Главная страница блога (показывает 5 последних опубликованных постов)."""
    model = Post
    template_name = 'blog/pages/index.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return (
            Post.objects.filter(status="published")
            .select_related('category', 'author')
            .prefetch_related('tags', 'viewed_by_users', 'bookmarked_by_users')
            .order_by('-created_at')[:5]
        )


class PostListView(ListView):
    """Страница со списком всех опубликованных постов с бесконечной прокруткой."""
    context_object_name = 'posts'
    template_name = 'blog/pages/post_list.html'
    posts_per_batch = 4

    def get_queryset(self):
        self.posts_queryset = (
            Post.objects.filter(status="published")
            .select_related('category', 'author')
            .prefetch_related('tags', 'viewed_by_users', 'bookmarked_by_users')
            .order_by('-created_at')
        )
        return self.posts_queryset[:PostListView.posts_per_batch]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["has_more_posts"] = self.posts_queryset.count() > PostListView.posts_per_batch
        context["posts_per_batch"] = PostListView.posts_per_batch
        return context


def load_more_posts_view(request):
    """AJAX-подгрузка следующей порции постов при прокрутке."""
    offset = int(request.GET.get("offset", 0))
    posts_queryset = (
        Post.objects.filter(status="published")
        .select_related('category', 'author')
        .prefetch_related('tags', 'viewed_by_users', 'bookmarked_by_users')
        .order_by('-created_at')
    )
    posts = posts_queryset[offset:offset + PostListView.posts_per_batch]
    posts_html = ''.join(
        [
            render_to_string("blog/includes/post_container.html", {"post": post}, request)
            for post in posts
        ]
    )
    has_more_posts = offset + PostListView.posts_per_batch < posts_queryset.count()
    return JsonResponse({
        'html': posts_html,
        'has_more': has_more_posts
    })


class CategoryPostsView(ListView):
    """Страница со списком постов конкретной категории."""
    context_object_name = 'posts'
    template_name = 'blog/pages/category_posts.html'
    paginate_by = 3

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        return (
            self.category.posts.filter(status='published')
            .select_related('category', 'author')
            .prefetch_related('tags', 'viewed_by_users', 'bookmarked_by_users')
            .order_by('-created_at')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class TagPostsView(ListView):
    """Страница со списком постов с определенным тегом."""
    model = Post
    template_name = 'blog/pages/tag_posts.html'
    context_object_name = 'posts'
    paginate_by = 3

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['tag_slug'])
        return (
            self.tag.posts.filter(status='published')
            .select_related('category', 'author')
            .prefetch_related('tags', 'viewed_by_users', 'bookmarked_by_users')
            .order_by('-created_at')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context


class PostsSearchView(ListView):
    """Страница поиска постов по заголовку, тексту, категориям и тегам."""
    template_name = "blog/pages/posts_search.html"
    context_object_name = 'posts'
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_performed'] = any(self.request.GET.keys())
        return context

    def get_queryset(self):
        search_query = self.request.GET.get("q")
        if search_query:
            queryset = (
                Post.objects.filter(status="published")
                .select_related('category', 'author')
                .prefetch_related('tags', 'viewed_by_users', 'bookmarked_by_users')
                .order_by("-created_at")
            )
            condition = Q(title__icontains=search_query) | Q(text__icontains=search_query)
            search_in_categories = self.request.GET.get("in_categories") == 'on'
            search_in_tags = self.request.GET.get("in_tags") == 'on'
            if search_in_categories:
                condition |= Q(category__name__icontains=search_query)
            if search_in_tags:
                condition |= Q(tags__name__icontains=search_query)
            return queryset.filter(condition).distinct()
        return Post.objects.none()


class PostDetailView(DetailView):
    """Страница детального просмотра одного поста с фиксацией просмотров и реакций."""
    model = Post
    slug_url_kwarg = 'post_slug'
    template_name = 'blog/pages/post_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        base_qs = Post.objects.select_related('category', 'author').prefetch_related('tags')
        if self.request.user.is_authenticated:
            return base_qs.filter(
                Q(status="published") | Q(author=self.request.user)
            )
        return base_qs.filter(status="published")

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        user = self.request.user
        session_key = f'post_{post.id}_viewed'
        
        if not self.request.session.get(session_key, False) and post.author != user:
            Post.objects.filter(id=post.id).update(views=F("views") + 1)
            post.views += 1
            self.request.session[session_key] = True
            
        if user.is_authenticated and user != post.author:
            post.viewed_by_users.add(user)
            
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        post = self.object
        context['is_liked'] = False
        context['is_disliked'] = False
        if user.is_authenticated:
            context['is_liked'] = post.liked_by_users.filter(id=user.id).exists()
            context['is_disliked'] = post.disliked_by_users.filter(id=user.id).exists()
        context['likes_count'] = post.liked_by_users.count()
        context['dislikes_count'] = post.disliked_by_users.count()
        return context


class PostAddView(LoginRequiredMixin, CreateView):
    """Страница добавления нового поста."""
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

        messages.success(self.request, 'Пост успешно добавлен!')
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


@require_POST
def post_like_toggle_view(request, post_id):
    """Переключение лайка поста через AJAX."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Требуется авторизация'}, status=401)
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    has_liked = post.liked_by_users.filter(id=user.id).exists()
    has_disliked = post.disliked_by_users.filter(id=user.id).exists()
    if has_liked:
        post.liked_by_users.remove(user)
        has_liked = False
    else:
        post.liked_by_users.add(user)
        has_liked = True
        if has_disliked:
            post.disliked_by_users.remove(user)
            has_disliked = False
    return JsonResponse({
        'likes_count': post.liked_by_users.count(),
        'dislikes_count': post.disliked_by_users.count(),
        'has_liked': has_liked,
        'has_disliked': has_disliked
    })


@require_POST
def post_dislike_toggle_view(request, post_id):
    """Переключение дизлайка поста через AJAX."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Требуется авторизация'}, status=401)
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    has_disliked = post.disliked_by_users.filter(id=user.id).exists()
    has_liked = post.liked_by_users.filter(id=user.id).exists()
    if has_disliked:
        post.disliked_by_users.remove(user)
        has_disliked = False
    else:
        post.disliked_by_users.add(user)
        has_disliked = True
        if has_liked:
            post.liked_by_users.remove(user)
            has_liked = False
    return JsonResponse({
        'dislikes_count': post.disliked_by_users.count(),
        'likes_count': post.liked_by_users.count(),
        'has_liked': has_liked,
        'has_disliked': has_disliked
    })


@require_POST
def post_favorite_toggle_view(request, post_id):
    """Добавление или удаление поста из избранного через AJAX."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Требуется авторизация'}, status=401)
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.bookmarked_by_users.all():
        post.bookmarked_by_users.remove(request.user)
        is_favorite = False
    else:
        post.bookmarked_by_users.add(request.user)
        is_favorite = True
    return JsonResponse({
        'is_favorite': is_favorite,
        'favorites_count': post.bookmarked_by_users.count()
    })
