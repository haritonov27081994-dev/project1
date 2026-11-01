from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Строку app_label = 'blog' мы удаляем, оставляем только оригинальные:
        verbose_name = 'пост'
        verbose_name_plural = 'посты'

    def __str__(self):
        return self.title
