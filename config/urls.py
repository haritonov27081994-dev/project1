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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.get_admin_urls() if hasattr(admin.site, 'get_admin_urls') else admin.site.urls), # Твой текущий список путей
    path('', include('apps.blog.urls', namespace='blog')),
    path('users/', include('apps.users.urls', namespace='users')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)