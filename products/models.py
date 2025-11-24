from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    """
    cat = Category.objects.get(id=1)
    products = cat.products.all()
    """
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.URLField(max_length=500, blank=True, help_text="Category image URL")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:category_products', kwargs={'slug': self.slug})


class Product(models.Model):
    """
    product = Product.objects.get(id=1)
    cat = product.category
    """
    SIZE_CHOICES = [
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', 'Double XL'),
    ]
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Optional discounted price")
    
    # Product details
    fabric = models.CharField(max_length=100, default="100% Cotton")
    color = models.CharField(max_length=50, default="White")
    available_sizes = models.CharField(max_length=100, default="S,M,L,XL", help_text="Comma-separated sizes")
    
    # Stock and availability
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, help_text="Show on homepage")
    
    # SEO and metadata
    meta_keywords = models.CharField(max_length=300, blank=True, help_text="SEO keywords")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category', 'is_available']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})
    
    @property
    def final_price(self):
        """Return discount price if available, otherwise regular price"""
        return self.discount_price if self.discount_price else self.price
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        if self.discount_price and self.price > self.discount_price:
            return int(((self.price - self.discount_price) / self.price) * 100)
        return 0
    
    @property
    def in_stock(self):
        """Check if product is in stock"""
        return self.stock > 0 and self.is_available
    
    def get_available_sizes_list(self):
        """Return list of available sizes"""
        return [size.strip() for size in self.available_sizes.split(',') if size.strip()]
    
    @classmethod
    def total_products(cls):
        """Return total number of images for the product"""
        return cls.objects.count()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField(max_length=500, help_text="Product image URL (e.g., from Unsplash)")
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False, help_text="Main product image")
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-is_primary']
    
    def __str__(self):
        return f"Image for {self.product.name}"
    
    def save(self, *args, **kwargs):
        if not self.alt_text:
            self.alt_text = self.product.name
        super().save(*args, **kwargs)
