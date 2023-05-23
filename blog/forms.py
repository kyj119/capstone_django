from .models import Comment
from django import forms

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('comment',)
        # exclude = ('post', 'author') 여러개 상속 받을때.