from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.views import LoginView as AuthLoginView, LogoutView as AuthLogoutView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView
from django.views.generic.list import MultipleObjectMixin

User = get_user_model()

class RegisterView(CreateView):
    """Регистрация нового пользователя."""
    template_name = 'users/pages/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('users:login')


class LoginView(AuthLoginView):
    """Вход в аккаунт на основе встроенного LoginView Django."""
    template_name = 'users/pages/login.html'
    authentication_form = AuthenticationForm

    def get_success_url(self):
        next_url = self.request.GET.get('next', settings.DEFAULT_LOGIN_REDIRECT_URL)
        if next_url == settings.DEFAULT_LOGIN_REDIRECT_URL:
            return reverse_lazy(next_url, kwargs={'username': self.request.user.username})
        return next_url


class LogoutView(AuthLogoutView):
    """Выход из аккаунта на основе встроенного LogoutView Django."""
    next_page = reverse_lazy('blog:home_page')


class ProfileView(DetailView, MultipleObjectMixin):
    """Страница профиля пользователя с пагинацией его постов по уроку."""
    model = User
    slug_url_kwarg = 'username'
    slug_field = 'username'
    template_name = 'users/pages/profile.html'
    paginate_by = 4  # Выводим по 4 поста на страницу профиля

    def get_context_data(self, **kwargs):
        # Получаем посты автора с сортировкой от новых к старым
        posts = self.object.posts.all().order_by('-created_at')
        
        # Передаем список в MultipleObjectMixin для пагинации
        context = super().get_context_data(object_list=posts, **kwargs)
        
        # Перекладываем запагинированные объекты в привычную переменную posts
        context['posts'] = context['object_list']
        del context['object_list']
        
        # Сохраняем profile_user для стабильности твоих HTML-шаблонов
        context['profile_user'] = self.object
        return context
