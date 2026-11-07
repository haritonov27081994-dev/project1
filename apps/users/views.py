from django.conf import settings
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView

User = get_user_model()

class RegisterView(CreateView):
    """Регистрация нового пользователя на основе CBV"""
    template_name = 'users/pages/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('users:login')

def login_view(request):
    """Вход в аккаунт с поддержкой умного редиректа next."""
    form = AuthenticationForm(data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            login(request, form.get_user())
            # Читаем параметр next из URL, если его нет — перенаправляем на дефолтный URL
            next_url = request.GET.get('next', settings.DEFAULT_LOGIN_REDIRECT_URL)
            
            if next_url == settings.DEFAULT_LOGIN_REDIRECT_URL:
                return redirect(next_url, username=request.user.username)
                
            return redirect(next_url)
            
    return render(request, 'users/pages/login.html', {'form': form})

@require_POST
def logout_view(request):
    """Безопасный выход из аккаунта (только через POST-запрос)."""
    logout(request)
    return redirect("blog:home_page")

def profile_view(request, username):
    """Страница профиля пользователя со списком его постов."""
    user = get_object_or_404(User, username=username)
    posts = user.posts.all()
    context = {
        'profile_user': user,  # Сохранено: имя переменной для стабильности шаблонов
        'posts': posts
    }
    return render(request, 'users/pages/profile.html', context)
