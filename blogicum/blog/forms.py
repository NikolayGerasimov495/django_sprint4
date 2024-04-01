from django import forms
from django.contrib.auth import get_user_model

from .models import Comment, Post

User = get_user_model()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author', 'created_at',)
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})}


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email',)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
