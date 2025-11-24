from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from accounts.models import Address
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import random
import string


class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    min_purchase_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    max_discount_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    usage_count = models.PositiveIntegerField(default=0)
    per_user_limit = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.discount_type}"
    
    def is_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False, "Coupon is not active"
        if now < self.valid_from:
            return False, "Coupon is not yet valid"
        if now > self.valid_to:
            return False, "Coupon has expired"
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False, "Coupon usage limit reached"
        return True, "Valid"
    
    def calculate_discount(self, subtotal):
        if self.discount_type == 'percentage':
            discount = subtotal * (self.discount_value / Decimal('100'))
            if self.max_discount_amount and discount > self.max_discount_amount:
                discount = self.max_discount_amount
        else:
            discount = self.discount_value
        
        return min(discount, subtotal)


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    order_number = models.CharField(max_length=100, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    
    # Delivery Address
    delivery_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name='delivery_orders')
    
    # Shipping address snapshot (in case address is deleted)
    shipping_full_name = models.CharField(max_length=200)
    shipping_phone = models.CharField(max_length=15)
    shipping_address_line1 = models.CharField(max_length=255)
    shipping_address_line2 = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_pincode = models.CharField(max_length=10)
    shipping_country = models.CharField(max_length=100, default='India')
    
    # Order totals
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Coupon
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    coupon_code = models.CharField(max_length=50, blank=True)
    
    # Order status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Additional info
    notes = models.TextField(blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_number} by {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        from datetime import datetime
        date_str = datetime.now().strftime('%Y%m%d')
        random_str = ''.join(random.choices(string.digits, k=8))
        return f"ORD-{date_str}-{random_str}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='order_items')
    
    # Product snapshot
    product_name = models.CharField(max_length=255)
    product_sku = models.CharField(max_length=100, blank=True)
    product_image = models.ImageField(upload_to='order_items/', blank=True)
    
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.quantity}x {self.product_name} in Order {self.order.order_number}"
    
    def save(self, *args, **kwargs):
        self.total = self.quantity * self.price
        super().save(*args, **kwargs)


class CouponUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coupon_usages')
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='coupon_usages')
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'coupon', 'order']
        ordering = ['-used_at']
    
    def __str__(self):
        return f"{self.user.username} used {self.coupon.code} on {self.order.order_number}"
