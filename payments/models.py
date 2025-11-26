from django.db import models
from django.contrib.auth.models import User
from orders.models import Order

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('razorpay', 'Razorpay'),
        ('cod', 'Cash on Delivery'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Razorpay specific fields
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    
    # Additional info
    failure_reason = models.TextField(blank=True, null=True)
    transaction_data = models.JSONField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Payment for Order {self.order.order_number} - {self.status}"
    
    def mark_as_success(self):
        """Mark payment as successful and update order status"""
        from django.utils import timezone
        self.status = 'success'
        self.paid_at = timezone.now()
        self.save()
        
        # Update order status
        self.order.status = 'confirmed'
        self.order.payment_status = 'paid'
        self.order.save()
    
    def mark_as_failed(self, reason=None):
        """Mark payment as failed"""
        self.status = 'failed'
        if reason:
            self.failure_reason = reason
        self.save()
        
        # Update order status
        self.order.status = 'failed'
        self.order.payment_status = 'failed'
        self.order.save()


class PaymentRefund(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]
    
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    razorpay_refund_id = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Refund for Payment {self.payment.id} - {self.status}"
