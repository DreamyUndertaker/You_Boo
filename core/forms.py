from django import forms
from django.forms import ModelForm
from .models import CustomUser, Profile, Rating, Review

class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        exclude = ['uuid']

class UserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name']


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['stars']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
        }
