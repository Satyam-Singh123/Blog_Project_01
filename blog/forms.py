from django import forms
from django.forms import fields
from . import models
from .models import User

class UserForm(forms.ModelForm):
    class Meta():
        model = models.User
        fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm):
    class Meta():
        model = models.UserProfile
        exclude = ('user',)

#1--------------------------------------------------------------
class PostForm(forms.ModelForm):

    class Meta:
        model = models.Post
        fields = ('author','title', 'text',)

        # widgets = {
        #     'title': forms.TextInput(attrs={'class': 'textinputclass'}),
        #     'text': forms.Textarea(attrs={'class': 'editable medium-editor-textarea postcontent'}),
        # }


class CommentForm(forms.ModelForm):

    class Meta:
        model = models.Comment
        fields = ('author', 'text',)

        # widgets = {

        #     'text': forms.Textarea(attrs={'class': 'editable medium-editor-textarea'}),
        # }
