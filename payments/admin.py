from django.contrib import admin
from .models import Payment, PaymentRefund


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'user', 'payment_method', 'amount', 'status', 'created_at']
    list_filter = ['payment_method', 'status', 'created_at']
    search_fields = ['order__order_number', 'user__username', 'razorpay_order_id', 'razorpay_payment_id']
    readonly_fields = ['created_at', 'updated_at', 'paid_at']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order', 'user')
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'amount', 'currency', 'status')
        }),
        ('Razorpay Details', {
            'fields': ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'paid_at')
        }),
        ('Additional Information', {
            'fields': ('failure_reason', 'transaction_data'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PaymentRefund)
class PaymentRefundAdmin(admin.ModelAdmin):
    list_display = ['id', 'payment', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['payment__razorpay_payment_id', 'razorpay_refund_id']
    readonly_fields = ['created_at', 'processed_at']
