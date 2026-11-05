from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from unidecode import unidecode

User = get_user_model()

class Post(models.Model):
    STATUS_CHOICES = (
        ('published', 'Опубликован'),
        ('draft', 'Черновик')
    )
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(max_length=200, unique=True, editable=False, verbose_name="Слаг")
    image = models.ImageField(upload_to="post_images/", null=True, blank=True)
    text = models.TextField(verbose_name="Текст")
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Статус")

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'

    def save(self, *args, **kwargs):
        if not self.slug:
            # Сначала генерируем базовый слаг из заголовка
            base_slug = slugify(unidecode(self.title))
            slug = base_slug
            counter = 1
            
            # Проверяем, есть ли уже пост с таким слагом. 
            # Если есть — добавляем к слагу дефис и цифру, пока не найдем свободный
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
                
            self.slug = slug
            
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
