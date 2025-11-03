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
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    phone = forms.CharField(max_length=20, required=False)
    
    class Meta:
        model = Profile
        fields = ['bio', 'gender', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us about yourself...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name


class AddressForm(forms.Form):
    """
    Form for adding/editing addresses
    """
    address_type = forms.ChoiceField(
        choices=[('home', 'Home'), ('work', 'Work'), ('other', 'Other')],
        required=True
    )
    full_name = forms.CharField(max_length=200, required=True)
    phone = forms.CharField(max_length=20, required=True)
    address_line1 = forms.CharField(max_length=255, required=True)
    address_line2 = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=100, required=True)
    state = forms.CharField(max_length=100, required=True)
    postal_code = forms.CharField(max_length=20, required=True)
    country = forms.CharField(max_length=100, initial='India', required=True)
    is_default = forms.BooleanField(required=False)
        