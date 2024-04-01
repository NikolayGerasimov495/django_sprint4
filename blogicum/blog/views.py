from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.urls import reverse
from django.utils import timezone


from .models import Category, Comment, Post
from .forms import CommentForm, PostForm, ProfileEditForm

User = get_user_model()

NUMBER_OF_PUBLICATIONS_PER_PAGE = 10


class PostMixin:
    model = Post
    template_name = 'blog/create.html'


class CommentMixin:
    model = Comment
    template_name = "blog/comment.html"
    form_class = CommentForm


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = NUMBER_OF_PUBLICATIONS_PER_PAGE

    def get_queryset(self):
        return (
            self.model.objects.select_related('location', 'author', 'category')
            .filter(is_published=True,
                    category__is_published=True,
                    pub_date__lte=timezone.now())
            .annotate(comment_count=Count("comment"))
            .order_by("-pub_date"))


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_object(self, queryset=None):
        post = get_object_or_404(
            self.model.objects.select_related('location', 'author', 'category'),
            pk=self.kwargs['id']
        )
        if post.is_published or self.request.user == post.author:
            return post
        raise Http404("Post not found")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comment.select_related('author')
        return context


class CategoryPostsListView(ListView):
    model = Post
    paginate_by = NUMBER_OF_PUBLICATIONS_PER_PAGE
    template_name = 'blog/category.html'

    def get_queryset(self):
        category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True)

        return (
            category.category_posts.select_related('location', 'author', 'category')
            .filter(is_published=True,
                    pub_date__lte=timezone.now())
            .annotate(comment_count=Count("comment"))
            .order_by("-pub_date"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category.objects.values('id', 'title', 'description'),
            slug=self.kwargs['category_slug'])
        return context


class PostCreateView(PostMixin, LoginRequiredMixin, CreateView):
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("blog:profile", args=[self.request.user])


class PostUpdateView(PostMixin, LoginRequiredMixin, UpdateView):
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'id': self.kwargs['post_id']})


class PostDeleteView(PostMixin, LoginRequiredMixin, DeleteView):
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse("blog:profile", kwargs={"username": self.request.user})


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = NUMBER_OF_PUBLICATIONS_PER_PAGE

    def get_queryset(self):
        return (
            self.model.objects.select_related('author')
            .filter(author__username=self.kwargs['username'])
            .annotate(comment_count=Count("comment"))
            .order_by("-pub_date"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username'])
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'blog/user.html'
    form_class = ProfileEditForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse("blog:profile", kwargs={"username": self.request.user})


class CommentCreateView(CommentMixin, LoginRequiredMixin, CreateView):
    post_obj = None

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(Post, id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_obj
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("blog:post_detail",
                       kwargs={'id': self.kwargs['post_id']})


class CommentBaseView(CommentMixin, LoginRequiredMixin):
    pk_url_kwarg = "comment_id"

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(
            Comment,
            pk=kwargs['comment_id'],
        )
        if comment.author != request.user:
            return redirect('blog:post_detail', id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("blog:post_detail",
                       kwargs={'id': self.kwargs['post_id']})


class CommentUpdateView(CommentBaseView, UpdateView):
    pass


class CommentDeleteView(CommentBaseView, DeleteView):
    pass
