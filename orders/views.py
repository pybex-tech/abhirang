from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
import json

from cart.models import Cart, CartItem
from accounts.models import Address
from .models import Order, OrderItem, Coupon, CouponUsage


@login_required
def checkout_view(request):
    """
    Checkout page view with address selection and coupon application
    """
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
        
        if not cart_items.exists():
            messages.warning(request, "Your cart is empty!")
            return redirect('cart:cart_detail')
        
    except Cart.DoesNotExist:
        messages.warning(request, "Your cart is empty!")
        return redirect('cart:cart_detail')
    
    # Get user addresses
    addresses = Address.objects.filter(user=request.user)
    default_address = addresses.filter(is_default=True).first()
    
    # Calculate cart totals
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    
    # Get applied coupon from session
    applied_coupon = None
    discount_amount = Decimal('0.00')
    coupon_code = request.session.get('applied_coupon')
    
    if coupon_code:
        try:
            applied_coupon = Coupon.objects.get(code=coupon_code)
            is_valid, message = applied_coupon.is_valid()
            
            if is_valid and subtotal >= applied_coupon.min_purchase_amount:
                discount_amount = applied_coupon.calculate_discount(subtotal)
            else:
                # Remove invalid coupon from session
                del request.session['applied_coupon']
                applied_coupon = None
        except Coupon.DoesNotExist:
            del request.session['applied_coupon']
    
    shipping_cost = Decimal('0.00')  # Free shipping for now
    tax_amount = Decimal('0.00')  # No tax for now
    total = subtotal - discount_amount + shipping_cost + tax_amount
    
    context = {
        'cart_items': cart_items,
        'addresses': addresses,
        'default_address': default_address,
        'subtotal': subtotal,
        'discount_amount': discount_amount,
        'shipping_cost': shipping_cost,
        'tax_amount': tax_amount,
        'total': total,
        'applied_coupon': applied_coupon,
    }
    
    return render(request, 'orders/checkout.html', context)


@login_required
def apply_coupon(request):
    """
    Apply coupon code via AJAX
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            coupon_code = data.get('coupon_code', '').strip().upper()
            
            if not coupon_code:
                return JsonResponse({
                    'success': False,
                    'message': 'Please enter a coupon code'
                })
            
            # Get cart subtotal
            try:
                cart = Cart.objects.get(user=request.user)
                cart_items = cart.items.all()
                subtotal = sum(item.product.price * item.quantity for item in cart_items)
            except Cart.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Cart is empty'
                })
            
            # Validate coupon
            try:
                coupon = Coupon.objects.get(code=coupon_code)
            except Coupon.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid coupon code'
                })
            
            # Check if coupon is valid
            is_valid, message = coupon.is_valid()
            if not is_valid:
                return JsonResponse({
                    'success': False,
                    'message': message
                })
            
            # Check minimum purchase amount
            if subtotal < coupon.min_purchase_amount:
                return JsonResponse({
                    'success': False,
                    'message': f'Minimum purchase amount of ₹{coupon.min_purchase_amount} required'
                })
            
            # Check per-user usage limit
            user_usage_count = CouponUsage.objects.filter(
                user=request.user,
                coupon=coupon
            ).count()
            
            if user_usage_count >= coupon.per_user_limit:
                return JsonResponse({
                    'success': False,
                    'message': 'You have already used this coupon'
                })
            
            # Calculate discount
            discount_amount = float(coupon.calculate_discount(subtotal))
            
            # Store coupon in session
            request.session['applied_coupon'] = coupon_code
            
            return JsonResponse({
                'success': True,
                'message': f'Coupon applied successfully! You saved ₹{discount_amount:.2f}',
                'discount_amount': discount_amount,
                'coupon_code': coupon_code,
                'discount_display': coupon.get_discount_display()
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid request'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })


@login_required
def remove_coupon(request):
    """
    Remove applied coupon via AJAX
    """
    if request.method == 'POST':
        if 'applied_coupon' in request.session:
            del request.session['applied_coupon']
        
        return JsonResponse({
            'success': True,
            'message': 'Coupon removed successfully'
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    })


@login_required
@transaction.atomic
def place_order(request):
    """
    Place order and create order records
    """
    if request.method == 'POST':
        try:
            # Get cart
            cart = Cart.objects.get(user=request.user)
            cart_items = cart.items.all()
            
            if not cart_items.exists():
                messages.error(request, "Your cart is empty!")
                return redirect('cart:cart_detail')
            
            # Get selected address
            address_id = request.POST.get('address_id')
            if not address_id:
                messages.error(request, "Please select a delivery address")
                return redirect('orders:checkout')
            
            address = get_object_or_404(Address, id=address_id, user=request.user)
            
            # Calculate totals
            subtotal = sum(item.product.price * item.quantity for item in cart_items)
            
            # Apply coupon if exists
            discount_amount = Decimal('0.00')
            applied_coupon = None
            coupon_code = request.session.get('applied_coupon')
            
            if coupon_code:
                try:
                    applied_coupon = Coupon.objects.get(code=coupon_code)
                    is_valid, message = applied_coupon.is_valid()
                    
                    if is_valid and subtotal >= applied_coupon.min_purchase_amount:
                        discount_amount = applied_coupon.calculate_discount(subtotal)
                    else:
                        applied_coupon = None
                except Coupon.DoesNotExist:
                    pass
            
            shipping_cost = Decimal('0.00')
            tax_amount = Decimal('0.00')
            total = subtotal - discount_amount + shipping_cost + tax_amount
            
            # Create order
            order = Order.objects.create(
                user=request.user,
                delivery_address=address,
                shipping_full_name=address.full_name,
                shipping_phone=address.phone,
                shipping_address_line1=address.address_line1,
                shipping_address_line2=address.address_line2,
                shipping_city=address.city,
                shipping_state=address.state,
                shipping_postal_code=address.postal_code,
                shipping_country=address.country,
                subtotal=subtotal,
                discount_amount=discount_amount,
                shipping_cost=shipping_cost,
                tax_amount=tax_amount,
                total_amount=total,
                coupon=applied_coupon,
                coupon_code=coupon_code if applied_coupon else '',
                notes=request.POST.get('notes', ''),
                status='pending',
                payment_status='pending'
            )
            
            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    product_price=cart_item.product.price,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
            
            # Track coupon usage
            if applied_coupon:
                CouponUsage.objects.create(
                    user=request.user,
                    coupon=applied_coupon,
                    order=order
                )
                # Increment usage count
                applied_coupon.usage_count += 1
                applied_coupon.save()
                
                # Remove from session
                if 'applied_coupon' in request.session:
                    del request.session['applied_coupon']
            
            # Clear cart
            cart_items.delete()
            
            messages.success(request, f'Order placed successfully! Order number: {order.order_number}')
            return redirect('orders:order_detail', order_number=order.order_number)
            
        except Cart.DoesNotExist:
            messages.error(request, "Your cart is empty!")
            return redirect('cart:cart_detail')
        except Exception as e:
            messages.error(request, f"Error placing order: {str(e)}")
            return redirect('orders:checkout')
    
    return redirect('orders:checkout')


@login_required
def order_detail(request, order_number):
    """
    Order detail view
    """
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    
    context = {
        'order': order,
    }
    
    return render(request, 'orders/order_detail.html', context)


@login_required
def order_list(request):
    """
    List all user orders
    """
    orders = Order.objects.filter(user=request.user)
    
    context = {
        'orders': orders,
    }
    
    return render(request, 'orders/order_list.html', context)
