from django.shortcuts import render


def home(request):
    """
    Home page view displaying hero section, deals, featured products, and brands
    """
    context = {
        'page_title': 'Home',
    }
    return render(request, 'core/index.html', context)
