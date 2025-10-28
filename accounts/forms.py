from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile


class CustomUserCreationForm(UserCreationForm):
    """
    Custom User Creation Form extending Django's UserCreationForm
    """
    pass


class CustomAuthenticationForm(AuthenticationForm):
    """
    Custom Authentication Form extending Django's AuthenticationForm
    """
    pass


class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating user profile information
    """
    class Meta:
        model = Profile
        fields = ['bio', 'gender', 'address_line1', 'address_line2', 
                  'city', 'state', 'postal_code', 'country', 'profile_picture']
        