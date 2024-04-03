from django.contrib.auth import get_user_model
from django.db import models

from core.models import PublishedModel
from .utils import PublishedPostQuerySet

TITLE_MAX_LENGTH = 256

User = get_user_model()


class Category(PublishedModel):
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=TITLE_MAX_LENGTH)
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        verbose_name='Идентификатор',
        unique=True,
        help_text=("Идентификатор страницы для URL; разрешены символы "
                   "латиницы, цифры, дефис и подчёркивание."))

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(PublishedModel):
    name = models.CharField(
        verbose_name='Название места',
        max_length=TITLE_MAX_LENGTH)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(PublishedModel):
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=TITLE_MAX_LENGTH)
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=("Если установить дату и время в будущем — можно делать "
                   "отложенные публикации."))
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='category_posts',
        verbose_name='Категория',
    )
    image = models.ImageField('Изображение', blank=True)

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-id']

    objects = PublishedPostQuerySet.as_manager()

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField(verbose_name='Текст комментария')
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comment', verbose_name='Публикация')
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Создано')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор')

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']

    def __str__(self):
        return f'Комметарий пользователя {self.author}'
