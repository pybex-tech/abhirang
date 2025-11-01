from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.views import View
from .models import Category, Product


class CategoryListView(View):
    """Display all active categories"""
    
    def get(self, request, *args, **kwargs):

        categories = Category.objects.filter(is_active=True)
        
        context = {
            'categories': categories,
            'page_title': 'All Collections'
        }
        
        return render(request, 'products/category_list.html', context)

    def post(self, request, *args, **kwargs):
        # Handle form submission for creating a new category
        pass

    def delete(self, request, *args, **kwargs):
        # Handle deletion of a category
        pass

    def put(self, request, *args, **kwargs):
        # Handle updating a category
        pass

    def patch(self, request, *args, **kwargs):
        # Handle partial update of a category
        pass


class ProductListView(View):
    """Display all available products with pagination"""
    
    def get(self, request, *args, **kwargs):
        products = Product.objects.filter(is_available=True)
        # .select_related('category').prefetch_related('images')
        # Pagination
        paginator = Paginator(products, 2)
        page_number = request.GET.get('page')
        
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        
        categories = Category.objects.filter(is_active=True)
        
        context = {
            'products': page_obj,
            'categories': categories,
            'page_title': 'All T-Shirts',
            'show_sidebar': True
        }
        
        return render(request, 'products/product_list.html', context)


class CategoryProductsView(View):
    """Display products filtered by category"""
    
    def get(self, request, slug, *args, **kwargs):
        category = get_object_or_404(Category, slug=slug, is_active=True)
        
        products = Product.objects.filter(
            category=category,
            is_available=True
        ).select_related('category').prefetch_related('images')
        
        # Pagination
        paginator = Paginator(products, 12)
        page_number = request.GET.get('page')
        
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        
        categories = Category.objects.filter(is_active=True)
        
        context = {
            'products': page_obj,
            'category': category,
            'categories': categories,
            'page_title': f'{category.name} Collection',
            'show_sidebar': True
        }
        
        return render(request, 'products/product_list.html', context)


class ProductDetailView(View):
    """Display detailed product information"""
    
    def get(self, request, slug, *args, **kwargs):
        product = get_object_or_404(
            Product.objects.select_related('category').prefetch_related('images'),
            slug=slug,
            is_available=True
        )
        
        # Get related products from same category
        related_products = Product.objects.filter(
            category=product.category,
            is_available=True
        ).exclude(id=product.id).prefetch_related('images')[:4]
        
        categories = Category.objects.filter(is_active=True)
        
        context = {
            'product': product,
            'related_products': related_products,
            'categories': categories,
            'page_title': product.name,
            'show_sidebar': False
        }
        
        return render(request, 'products/product_detail.html', context)


class ProductSearchView(View):
    """Search products by keywords"""
    
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '').strip()
        
        if query:
            # Search in name, description, and meta keywords
            products = Product.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(meta_keywords__icontains=query) |
                Q(category__name__icontains=query),
                is_available=True
            ).select_related('category').prefetch_related('images').distinct()
            
            # Pagination
            paginator = Paginator(products, 12)
            page_number = request.GET.get('page')
            
            try:
                page_obj = paginator.page(page_number)
            except PageNotAnInteger:
                page_obj = paginator.page(1)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)
        else:
            page_obj = Paginator(Product.objects.none(), 12).page(1)
        
        categories = Category.objects.filter(is_active=True)
        
        context = {
            'products': page_obj,
            'categories': categories,
            'query': query,
            'page_title': f'Search Results for "{query}"' if query else 'Search Products',
            'show_sidebar': True
        }
        
        return render(request, 'products/search_results.html', context)
