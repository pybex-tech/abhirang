from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic import ListView, DetailView, View
from .models import Category, Product

class MyView(View):
    
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        return render(request, 'products/myview.html', {'categories': categories})
    
def list_categories(request):
    categories = Category.objects.filter(is_active=True)
    return render(request, 'products/category_list.html', {'categories': categories})

class CategoryListView(ListView):
    """Display all active categories"""
    model = Category

class ProductListView(ListView):
    """Display all available products with pagination"""
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        return Product.objects.filter(
            is_available=True
        ).select_related('category').prefetch_related('images')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['page_title'] = 'All T-Shirts'
        context['show_sidebar'] = True
        return context


class CategoryProductsView(ListView):
    """Display products filtered by category"""
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        self.category = get_object_or_404(
            Category, 
            slug=self.kwargs['slug'], 
            is_active=True
        )
        return Product.objects.filter(
            category=self.category,
            is_available=True
        ).select_related('category').prefetch_related('images')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = Category.objects.filter(is_active=True)
        context['page_title'] = f'{self.category.name} Collection'
        context['show_sidebar'] = True
        return context


class ProductDetailView(DetailView):
    """Display detailed product information"""
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Product.objects.filter(
            is_available=True
        ).select_related('category').prefetch_related('images')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get related products from same category
        context['related_products'] = Product.objects.filter(
            category=self.object.category,
            is_available=True
        ).exclude(id=self.object.id).prefetch_related('images')[:4]
        
        context['categories'] = Category.objects.filter(is_active=True)
        context['page_title'] = self.object.name
        context['show_sidebar'] = False
        return context


class ProductSearchView(ListView):
    """Search products by keywords"""
    model = Product
    template_name = 'products/search_results.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        
        if query:
            # Search in name, description, and meta keywords
            return Product.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(meta_keywords__icontains=query) |
                Q(category__name__icontains=query),
                is_available=True
            ).select_related('category').prefetch_related('images').distinct()
        
        return Product.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        
        context['categories'] = Category.objects.filter(is_active=True)
        context['query'] = query
        context['page_title'] = f'Search Results for "{query}"' if query else 'Search Products'
        context['show_sidebar'] = True
        return context
