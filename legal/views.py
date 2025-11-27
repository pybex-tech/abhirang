from django.shortcuts import render


def terms_of_service(request):
    """Terms of Service page"""
    return render(request, 'legal/terms_of_service.html')


def privacy_policy(request):
    """Privacy Policy page"""
    return render(request, 'legal/privacy_policy.html')


def refund_policy(request):
    """Refund Policy page"""
    return render(request, 'legal/refund_policy.html')


def cancellation_policy(request):
    """Cancellation Policy page"""
    return render(request, 'legal/cancellation_policy.html')


def shipping_policy(request):
    """Shipping Policy page"""
    return render(request, 'legal/shipping_policy.html')
