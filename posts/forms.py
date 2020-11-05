from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = (
            'author',
        )
        fields = '__all__'


# class CommentForm(forms.ModelForm):
#     class Meta:
#         model = Comment
#         fields = '__all__' #['text']
#         # help_texts = {
#         #     'text': 'Текст',
#         # }
#
#     text = forms.CharField(widget=forms.Textarea)
class CommentForm(forms.ModelForm):
    """ form for adding a comment to a post """
    class Meta:
        """ bind form to Comment model and add field 'text' """
        model = Comment
        fields = ('text',)
        labels = {'text': 'Комментарий',}
        widgets = {'text': forms.Textarea({'rows': 3})}
