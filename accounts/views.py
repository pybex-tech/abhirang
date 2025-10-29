from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileUpdateForm
from .models import Profile


def signup_view(request):
    """
    Function-based view for user registration
    """
    if request.user.is_authenticated:
        return redirect('products:product_list')
    
    if request.method == 'POST':
        print(request.POST)
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Auto-login after signup
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to Abhirang!')
            return redirect('products:product_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/signup.html', {'form': form, 'title': 'Sign Up'})


def login_view(request):
    """
    Function-based view for user login
    """
    if request.user.is_authenticated:
        return redirect('products:product_list')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect("products:product_list")
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form, 'title': 'Login'})


def logout_view(request):
    """
    Function-based view for user logout
    """
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('products:product_list')


@login_required
def profile_view(request):
    """
    Function-based view for viewing and updating user profile
    """
    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'profile_form': profile_form,
        'title': 'Profile'
    }
    
    return render(request, 'accounts/profile.html', context)
