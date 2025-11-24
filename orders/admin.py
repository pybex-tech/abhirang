from django.contrib import admin
from .models import Coupon, Order, OrderItem, CouponUsage


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'quantity', 'price', 'total')
    can_delete = False


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'is_active', 'valid_from', 'valid_to', 'usage_count', 'usage_limit')
    list_filter = ('discount_type', 'is_active', 'valid_from', 'valid_to')
    search_fields = ('code',)
    readonly_fields = ('usage_count', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'discount_type', 'discount_value', 'is_active')
        }),
        ('Restrictions', {
            'fields': ('min_purchase_amount', 'max_discount_amount', 'usage_limit', 'per_user_limit')
        }),
        ('Validity Period', {
            'fields': ('valid_from', 'valid_to')
        }),
        ('Usage Statistics', {
            'fields': ('usage_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'payment_status', 'total_amount', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('order_number', 'user__username', 'user__email', 'shipping_full_name', 'shipping_phone')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'payment_status')
        }),
        ('Shipping Address', {
            'fields': ('delivery_address', 'shipping_full_name', 'shipping_phone', 
                      'shipping_address_line1', 'shipping_address_line2', 
                      'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country')
        }),
        ('Order Totals', {
            'fields': ('subtotal', 'discount_amount', 'shipping_cost', 'tax_amount', 'total_amount')
        }),
        ('Coupon', {
            'fields': ('coupon', 'coupon_code'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes', 'tracking_number'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'confirmed_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'quantity', 'price', 'total')
    list_filter = ('created_at',)
    search_fields = ('order__order_number', 'product_name')
    readonly_fields = ('created_at',)


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'coupon', 'order', 'used_at')
    list_filter = ('used_at',)
    search_fields = ('user__username', 'coupon__code', 'order__order_number')
    readonly_fields = ('used_at',)
