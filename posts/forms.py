from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = (
            'author',
        )
        fields = '__all__'


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', ]
        labels = {
            'text': 'Комментарий',
        }
        widgets = {
            'text': forms.Textarea({'rows': 3})
        }
