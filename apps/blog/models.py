from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
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
    category = models.ForeignKey(
        'Category',
        related_name='posts',
        on_delete=models.CASCADE,
        verbose_name="Категория"
    )
    tags = models.ManyToManyField("Tag", related_name='posts', blank=True, verbose_name='Теги')
    image = models.ImageField(upload_to="post_images/", null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    text = models.TextField(verbose_name="Текст")
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Статус")
    views = models.PositiveIntegerField(default=0, verbose_name="Просмотры")
    viewed_by_users = models.ManyToManyField(
        User, 
        related_name='viewed_posts',
        blank=True,
        verbose_name="Просмотрено пользователями"
    )
    liked_by_users = models.ManyToManyField(
        User,
        related_name="liked_posts",
        blank=True,
        verbose_name="Лайки"
    )
    disliked_by_users = models.ManyToManyField(
        User,
        related_name="disliked_posts",
        blank=True,
        verbose_name="Дизлайки"
    )
    bookmarked_by_users = models.ManyToManyField(
        User,
        related_name="bookmarked_posts",
        blank=True,
        verbose_name="В избранном у"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'post_slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(unidecode(self.title))
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    slug = models.SlugField(max_length=50, unique=True, editable=False)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = "категории"

    def get_absolute_url(self):
        return reverse('blog:category_posts', kwargs={'category_slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    slug = models.SlugField(max_length=50, unique=True, editable=False)

    class Meta:
        verbose_name = "тег"
        verbose_name_plural = "теги"

    def get_absolute_url(self):
        return reverse('blog:tag_posts', kwargs={'tag_slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(unidecode(self.name))
            slug = base_slug
            counter = 1
            while Tag.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f'#{self.name}'
