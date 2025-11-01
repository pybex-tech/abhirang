from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    """Inline for cart items in cart admin"""
    model = CartItem
    extra = 0
    readonly_fields = ['added_at', 'updated_at', 'subtotal', 'price']
    fields = ['product', 'quantity', 'size', 'price', 'subtotal', 'added_at']
    
    def subtotal(self, obj):
        return f"₹{obj.subtotal}"
    subtotal.short_description = 'Subtotal'
    
    def price(self, obj):
        return f"₹{obj.price}"
    price.short_description = 'Price'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin for Cart model"""
    list_display = ['user', 'total_items', 'cart_subtotal', 'cart_total', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'total_items', 'cart_subtotal', 'cart_total', 'total_discount']
    inlines = [CartItemInline]
    
    def cart_subtotal(self, obj):
        return f"₹{obj.subtotal}"
    cart_subtotal.short_description = 'Subtotal'
    cart_subtotal.admin_order_field = 'id'
    
    def cart_total(self, obj):
        return f"₹{obj.total}"
    cart_total.short_description = 'Total'
    
    def total_discount(self, obj):
        return f"₹{obj.total_discount}"
    total_discount.short_description = 'Discount'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin for CartItem model"""
    list_display = ['id', 'cart_user', 'product', 'quantity', 'size', 'item_price', 'item_subtotal', 'added_at']
    list_filter = ['added_at', 'updated_at', 'size']
    search_fields = ['product__name', 'cart__user__username']
    readonly_fields = ['added_at', 'updated_at', 'price', 'subtotal', 'discount_amount']
    list_select_related = ['cart__user', 'product']
    
    def cart_user(self, obj):
        return obj.cart.user.username
    cart_user.short_description = 'User'
    cart_user.admin_order_field = 'cart__user__username'
    
    def item_price(self, obj):
        return f"₹{obj.price}"
    item_price.short_description = 'Price'
    
    def item_subtotal(self, obj):
        return f"₹{obj.subtotal}"
    item_subtotal.short_description = 'Subtotal'
