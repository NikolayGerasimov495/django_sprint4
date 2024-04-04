from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .forms import CommentForm, PostForm, ProfileEditForm
from .mixins import (CommentBaseViewMixin, CommentMixin, DispatchMixin,
                     ProfileGetSuccessUrlMixin, PostDetailGetSuccessUrlMixin,
                     PostMixin)
from .models import Category, Post

User = get_user_model()

NUMBER_OF_PUBLICATIONS_PER_PAGE = 10


class PostListView(ListView):
    """Представление для списка публикаций"""

    model = Post
    template_name = 'blog/index.html'
    paginate_by = NUMBER_OF_PUBLICATIONS_PER_PAGE

    def get_queryset(self):
        return (
            self.model.objects.post_select_related()
            .published_filter()
            .published_count_order())


class PostDetailView(LoginRequiredMixin, DetailView):
    """Представление публикации"""

    model = Post
    template_name = 'blog/detail.html'

    def get_object(self, queryset=None):
        post = get_object_or_404(
            self.model.objects.post_select_related(),
            pk=self.kwargs['id']
        )
        if post.is_published or self.request.user == post.author:
            return post
        raise Http404('Post not found')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class CategoryPostsListView(ListView):
    """Представление категории публикаций"""

    model = Post
    paginate_by = NUMBER_OF_PUBLICATIONS_PER_PAGE
    template_name = 'blog/category.html'

    def get_queryset(self):
        category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True)

        return (
            category.category_posts.post_select_related()
            .published_filter()
            .published_count_order())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category.objects.values('id', 'title', 'description'),
            slug=self.kwargs['category_slug'])
        return context


class PostCreateView(PostMixin, ProfileGetSuccessUrlMixin, LoginRequiredMixin,
                     CreateView):
    """Представление для создания новой публикации"""

    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(PostDetailGetSuccessUrlMixin, PostMixin, DispatchMixin,
                     LoginRequiredMixin, UpdateView):
    """Представление для редактирования публикации"""

    form_class = PostForm
    pk_url_kwarg = 'post_id'


class PostDeleteView(PostMixin, DispatchMixin, ProfileGetSuccessUrlMixin,
                     LoginRequiredMixin, DeleteView):
    """Представление для удаления публикации"""

    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context


class ProfileListView(ListView):
    """Представление списка публикаций пользователя"""

    model = Post
    template_name = 'blog/profile.html'
    paginate_by = NUMBER_OF_PUBLICATIONS_PER_PAGE

    def get_queryset(self):
        return (
            self.model.objects.post_select_related()
            .filter(author__username=self.kwargs['username'])
            .published_count_order())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username'])
        return context


class ProfileUpdateView(ProfileGetSuccessUrlMixin, LoginRequiredMixin, UpdateView):
    """Представление для изменений данных пользователя в профиле"""

    template_name = 'blog/user.html'
    form_class = ProfileEditForm

    def get_object(self, queryset=None):
        return self.request.user


class CommentCreateView(PostDetailGetSuccessUrlMixin, CommentMixin,
                        LoginRequiredMixin, CreateView):
    """Представление для создания комментария"""

    post_obj = None

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(Post, id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_obj
        return super().form_valid(form)


class CommentUpdateView(CommentBaseViewMixin, UpdateView):
    """Представление для редактировани комментария"""

    pass


class CommentDeleteView(CommentBaseViewMixin, DeleteView):
    """Представление для удаления комментария"""

    pass
