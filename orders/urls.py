from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('remove-coupon/', views.remove_coupon, name='remove_coupon'),
    path('place-order/', views.place_order, name='place_order'),
    path('order/<str:order_number>/', views.order_detail, name='order_detail'),
    path('my-orders/', views.order_list, name='order_list'),
]
