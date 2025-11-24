from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from decimal import Decimal


class Cart(models.Model):
    """Shopping cart for each user"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Shopping Cart'
        verbose_name_plural = 'Shopping Carts'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Cart for {self.user.username}"
    
    @property
    def subtotal(self):
        """Calculate cart subtotal (sum of all item subtotals)"""
        return sum(item.subtotal for item in self.items.all())
    
    @property
    def total_items(self):
        """Total number of items in cart"""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_discount(self):
        """Total discount amount"""
        return sum(item.discount_amount for item in self.items.all())
    
    @property
    def total(self):
        """Final total after discounts"""
        return self.subtotal
    
    def clear(self):
        """Remove all items from cart"""
        self.items.all().delete()


class CartItem(models.Model):
    """Individual items in the shopping cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=10, blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        ordering = ['-added_at']
        unique_together = ['cart', 'product', 'size']
    
    def __str__(self):
        size_info = f" ({self.size})" if self.size else ""
        return f"{self.quantity}x {self.product.name}{size_info} in {self.cart.user.username}'s cart"
    
    @property
    def price(self):
        """Get the current price of the product"""
        return self.product.final_price
    
    @property
    def original_price(self):
        """Original price before discount"""
        return self.product.price
    
    @property
    def subtotal(self):
        """Calculate subtotal for this cart item"""
        return self.price * self.quantity
    
    @property
    def original_subtotal(self):
        """Original subtotal before discount"""
        return self.original_price * self.quantity
    
    @property
    def discount_amount(self):
        """Discount amount for this item"""
        if self.product.discount_price:
            return (self.original_price - self.price) * self.quantity
        return Decimal('0.00')
    
    @property
    def has_discount(self):
        """Check if item has discount"""
        return self.product.discount_price is not None
    
    def increase_quantity(self, amount=1):
        """Increase item quantity"""
        self.quantity += amount
        self.save()
    
    def decrease_quantity(self, amount=1):
        """Decrease item quantity"""
        if self.quantity > amount:
            self.quantity -= amount
            self.save()
        else:
            self.delete()

    def add_product_to_cart(user, product, quantity=1, size=None):
        """Utility method to add a product to user's cart"""
        cart, created = Cart.objects.get_or_create(user=user)
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            size=size,
            defaults={'quantity': quantity}
        )
        if not item_created:
            cart_item.increase_quantity(quantity)
        return cart_item

