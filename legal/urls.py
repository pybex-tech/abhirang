from django.urls import path
from . import views

app_name = 'legal'

urlpatterns = [
    path('contact-us/', views.contact_us, name='contact_us'),
    path('faq/', views.faq, name='faq'),
    path('track-orders/', views.track_orders, name='track_orders'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('refund-policy/', views.refund_policy, name='refund_policy'),
    path('cancellation-policy/', views.cancellation_policy, name='cancellation_policy'),
    path('shipping-policy/', views.shipping_policy, name='shipping_policy'),
]
