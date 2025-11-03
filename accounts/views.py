from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
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
    tab = request.GET.get('tab', 'overview')
    
    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if profile_form.is_valid():
            # Update user fields
            user = request.user
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.save()
            
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    # Get user's addresses
    from .models import Address
    addresses = Address.objects.filter(user=request.user)
    
    # Get user's orders (if order model exists)
    orders = []
    try:
        from cart.models import Order
        orders = Order.objects.filter(user=request.user).order_by('-created_at')[:10]
    except:
        pass
    
    context = {
        'profile_form': profile_form,
        'addresses': addresses,
        'orders': orders,
        'active_tab': tab,
        'title': 'Profile'
    }
    
    return render(request, 'accounts/profile.html', context)


@login_required
def change_password_view(request):
    """
    View for changing user password
    """
    from django.contrib.auth.forms import PasswordChangeForm
    from django.contrib.auth import update_session_auth_hash
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:profile') + '?tab=security'
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return redirect('accounts:profile') + '?tab=security'


@login_required
def change_email_view(request):
    """
    View for changing user email
    """
    if request.method == 'POST':
        new_email = request.POST.get('email')
        if new_email:
            request.user.email = new_email
            request.user.save()
            messages.success(request, 'Your email was successfully updated!')
        return redirect('accounts:profile') + '?tab=security'
    
    return redirect('accounts:profile')


@login_required
def add_address_view(request):
    """
    View for adding a new address
    """
    from .models import Address
    
    if request.method == 'POST':
        address = Address(user=request.user)
        address.address_type = request.POST.get('address_type', 'home')
        address.full_name = request.POST.get('full_name', '')
        address.phone = request.POST.get('phone', '')
        address.address_line1 = request.POST.get('address_line1', '')
        address.address_line2 = request.POST.get('address_line2', '')
        address.city = request.POST.get('city', '')
        address.state = request.POST.get('state', '')
        address.postal_code = request.POST.get('postal_code', '')
        address.country = request.POST.get('country', 'India')
        address.is_default = request.POST.get('is_default') == 'on'
        address.save()
        
        messages.success(request, 'Address added successfully!')
        return redirect('accounts:profile') + '?tab=addresses'
    
    return redirect('accounts:profile') + '?tab=addresses'


@login_required
def delete_address_view(request, address_id):
    """
    View for deleting an address
    """
    from .models import Address
    
    try:
        address = Address.objects.get(id=address_id, user=request.user)
        address.delete()
        messages.success(request, 'Address deleted successfully!')
    except Address.DoesNotExist:
        messages.error(request, 'Address not found.')
    
    return redirect('accounts:profile') + '?tab=addresses'
