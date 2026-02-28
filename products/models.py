from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    description = models.TextField(blank=True)
    is_featured = models.BooleanField(
        default=True, 
        verbose_name="Is New (Show on Home)",
        help_text="Check this to show this category on the homepage"
    )

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_new = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    stock = models.PositiveIntegerField(default=0)
    badge = models.CharField(max_length=50, blank=True)  # e.g., 'HOT', 'SALE'

    def __str__(self):
        return self.name

    def get_image_url(self):
        """Return image URL or placeholder"""
        if self.image and hasattr(self.image, 'url'):
            try:
                return self.image.url
            except:
                return '/static/images/product_placeholder.png'
        return '/static/images/product_placeholder.png'

    @property
    def discount_percentage(self):
        if self.original_price and self.original_price > self.price:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0
    
    def average_rating(self):
        """Calculate average rating from reviews"""
        reviews = self.reviews.filter(is_hidden=False)
        if reviews.exists():
            total_rating = sum(r.rating for r in reviews)
            return round(total_rating / reviews.count(), 1)
        return None
    
    def review_count(self):
        """Return total number of reviews"""
        return self.reviews.filter(is_hidden=False).count()

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='gallery_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product.name}"


class Review(models.Model):
    """
    Product Review Model - Following Amazon/Flipkart Pattern
    - Only delivered orders can be reviewed
    - One review per product per order
    - Reviews are immutable (cannot be edited/deleted for audit safety)
    """
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]

    user = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    order = models.ForeignKey('orders.Order', on_delete=models.PROTECT)

    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField(max_length=500)

    created_at = models.DateTimeField(auto_now_add=True)
    
    # Future features
    is_verified_purchase = models.BooleanField(default=True)
    is_hidden = models.BooleanField(default=False)  # For admin moderation

    class Meta:
        unique_together = ('user', 'product', 'order')
        ordering = ['-created_at']
        verbose_name = 'Product Review'
        verbose_name_plural = 'Product Reviews'

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}★)"
    
    def get_star_display(self):
        """Return star symbols for display"""
        return '★' * self.rating + '☆' * (5 - self.rating)
