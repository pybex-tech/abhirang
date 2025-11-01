from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from products.models import Product
from .models import Cart, CartItem


@method_decorator(login_required, name='dispatch')
class CartView(View):
    """Display user's shopping cart"""
    
    def get(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.items.select_related('product').prefetch_related('product__images')
        
        context = {
            'cart': cart,
            'cart_items': cart_items,
            'page_title': 'Shopping Cart'
        }
        
        return render(request, 'cart/cart.html', context)


@method_decorator(login_required, name='dispatch')
class AddToCartView(View):
    """Add a product to cart"""
    
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        size = request.POST.get('size', '')
        
        product = get_object_or_404(Product, id=product_id, is_available=True)
        
        # Get or create cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Check if item already exists in cart
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            size=size if size else None,
            defaults={'quantity': quantity}
        )
        
        if not item_created:
            # Item exists, increase quantity
            cart_item.quantity += quantity
            cart_item.save()
            messages.success(request, f'Updated {product.name} quantity in cart')
        else:
            messages.success(request, f'Added {product.name} to cart')
        
        # Return JSON for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Added {product.name} to cart',
                'cart_total_items': cart.total_items
            })
        
        return redirect('cart:view_cart')


@method_decorator(login_required, name='dispatch')
class RemoveFromCartView(View):
    """Remove an item from cart"""
    
    def post(self, request, item_id, *args, **kwargs):
        cart_item = get_object_or_404(
            CartItem, 
            id=item_id, 
            cart__user=request.user
        )
        
        product_name = cart_item.product.name
        cart_item.delete()
        
        messages.success(request, f'Removed {product_name} from cart')
        
        # Return JSON for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart = Cart.objects.get(user=request.user)
            return JsonResponse({
                'success': True,
                'message': f'Removed {product_name} from cart',
                'cart_total_items': cart.total_items,
                'cart_subtotal': float(cart.subtotal),
                'cart_total': float(cart.total)
            })
        
        return redirect('cart:view_cart')


@method_decorator(login_required, name='dispatch')
class UpdateCartItemView(View):
    """Update cart item quantity"""
    
    def post(self, request, item_id, *args, **kwargs):
        cart_item = get_object_or_404(
            CartItem, 
            id=item_id, 
            cart__user=request.user
        )
        
        action = request.POST.get('action')
        quantity = request.POST.get('quantity')
        
        if action == 'increase':
            cart_item.increase_quantity()
            messages.success(request, f'Increased quantity of {cart_item.product.name}')
        elif action == 'decrease':
            cart_item.decrease_quantity()
            messages.success(request, f'Decreased quantity of {cart_item.product.name}')
        elif quantity:
            new_quantity = int(quantity)
            if new_quantity > 0:
                cart_item.quantity = new_quantity
                cart_item.save()
                messages.success(request, f'Updated quantity of {cart_item.product.name}')
            else:
                cart_item.delete()
                messages.success(request, f'Removed {cart_item.product.name} from cart')
        
        # Return JSON for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart = Cart.objects.get(user=request.user)
            try:
                # Item might have been deleted
                cart_item.refresh_from_db()
                item_data = {
                    'quantity': cart_item.quantity,
                    'subtotal': float(cart_item.subtotal)
                }
            except CartItem.DoesNotExist:
                item_data = {'deleted': True}
            
            return JsonResponse({
                'success': True,
                'item': item_data,
                'cart_total_items': cart.total_items,
                'cart_subtotal': float(cart.subtotal),
                'cart_total': float(cart.total)
            })
        
        return redirect('cart:view_cart')


@method_decorator(login_required, name='dispatch')
class ClearCartView(View):
    """Clear all items from cart"""
    
    def post(self, request, *args, **kwargs):
        try:
            cart = Cart.objects.get(user=request.user)
            cart.clear()
            messages.success(request, 'Cart cleared successfully')
        except Cart.DoesNotExist:
            messages.info(request, 'Your cart is already empty')
        
        return redirect('cart:view_cart')
