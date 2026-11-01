from django.contrib import admin
from .models import Post  # Обязательно должна быть точка перед models!

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    pass
