from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('initiate/<str:order_number>/', views.initiate_payment, name='initiate_payment'),
    path('callback/', views.payment_callback, name='payment_callback'),
    path('success/<str:order_number>/', views.payment_success, name='payment_success'),
    path('failed/<str:order_number>/', views.payment_failed, name='payment_failed'),
    path('webhook/', views.razorpay_webhook, name='razorpay_webhook'),
]
