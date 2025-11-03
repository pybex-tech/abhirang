from django.urls import path
from .views import (
    signup_view, login_view, logout_view, profile_view,
    change_password_view, change_email_view,
    add_address_view, delete_address_view
)

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # Profile Management
    path('profile/', profile_view, name='profile'),
    path('profile/change-password/', change_password_view, name='change_password'),
    path('profile/change-email/', change_email_view, name='change_email'),
    
    # Address Management
    path('profile/address/add/', add_address_view, name='add_address'),
    path('profile/address/<int:address_id>/delete/', delete_address_view, name='delete_address'),
]
