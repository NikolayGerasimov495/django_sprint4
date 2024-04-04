from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from .forms import CommentForm
from .models import Comment, Post


class PostMixin:
    """Миксин для работы с публикациями"""

    model = Post
    template_name = 'blog/create.html'


class CommentMixin:
    """Миксин для работы с комментариями"""

    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm


class CommentBaseViewMixin(CommentMixin, LoginRequiredMixin):
    """Базовое представление для работы с комментариями"""

    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(
            Comment,
            pk=kwargs['comment_id'],
        )
        if comment.author != request.user:
            return redirect('blog:post_detail', id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'id': self.kwargs['post_id']})


class ProfileGetSuccessUrlMixin:

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class PostDetailGetSuccessUrlMixin:

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'id': self.kwargs['post_id']})


class DispatchMixin:

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)
