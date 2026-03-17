from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Feedback

# Form to edit username and email (User model)
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']


# Form to edit extra profile fields (UserProfile model)
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['address', 'phone', 'payment_option']


# Signup form (extends Django's UserCreationForm)
class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


# Feedback form
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["message"]
