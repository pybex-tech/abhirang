from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.CartView.as_view(), name='view_cart'),
    path('add/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('remove/<int:item_id>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('update/<int:item_id>/', views.UpdateCartItemView.as_view(), name='update_cart_item'),
    path('clear/', views.ClearCartView.as_view(), name='clear_cart'),
]
