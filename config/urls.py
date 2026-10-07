"""
URL configuration for config project.
The `urlpatterns` list routes URLs to views. For more information please see:
    https://djangoproject.com
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path

# Временная функция для отображения текста на главной странице
def home_page_view(request):
    return HttpResponse("<h1>Главная страница</h1>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls')), # Подключаем маршруты блога по адресу /blog/
    path('', home_page_view),            # Отображаем нашу функцию на главной странице (корень сайта)
]