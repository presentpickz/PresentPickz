from django.db import models
from django.conf import settings
from products.models import Product
from PIL import Image
import os

class Wishlist(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, related_name='wishlisted_by')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Wishlist"

class Address(models.Model):
    ADDRESS_TYPE_CHOICES = (
        ('HOME', 'Home'),
        ('WORK', 'Work'),
        ('OTHER', 'Other'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES, default='HOME')
    is_default = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - {self.address_type}"
        
    class Meta:
        verbose_name_plural = 'Addresses'

class UserProfile(models.Model):
    """Extended user profile for additional fields like profile photo"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    profile_photo = models.ImageField(
        upload_to='profile_photos/', 
        blank=True, 
        null=True,
        help_text='Upload a profile photo (max 2MB, JPG/PNG)'
    )
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize image if it exists
        if self.profile_photo:
            img_path = self.profile_photo.path
            if os.path.exists(img_path):
                img = Image.open(img_path)
                
                # Convert RGBA to RGB if needed
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                
                # Resize to max 500x500 while maintaining aspect ratio
                max_size = (500, 500)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                img.save(img_path, quality=85, optimize=True)
    
    def delete_photo(self):
        """Delete the profile photo file"""
        if self.profile_photo:
            if os.path.isfile(self.profile_photo.path):
                os.remove(self.profile_photo.path)
            self.profile_photo = None
            self.save()
    
    @property
    def get_initials(self):
        """Get user initials for avatar"""
        if self.user.first_name:
            return self.user.first_name[0].upper()
        return self.user.username[0].upper()

import secrets
from django.utils import timezone
from datetime import timedelta


class PasswordResetToken(models.Model):
    """
    Secure password reset token model.
    Tokens are single-use, time-limited, and tracked for security auditing.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='reset_tokens'
    )
    token = models.CharField(
        max_length=64, 
        unique=True, 
        db_index=True,
        help_text='Cryptographically secure URL-safe token'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    
    # Security tracking
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.token:
            # Generate cryptographically secure token
            self.token = secrets.token_urlsafe(32)
        
        if not self.expires_at:
            # Token valid for 1 hour
            self.expires_at = timezone.now() + timedelta(hours=1)
        
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if token has expired"""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Check if token is valid (not used and not expired)"""
        return not self.is_used and not self.is_expired()
    
    def mark_as_used(self):
        """Mark token as used"""
        self.is_used = True
        self.used_at = timezone.now()
        self.save()
    
    @classmethod
    def create_for_user(cls, user, ip_address=None, user_agent=None):
        """
        Create a new reset token for a user.
        Invalidates all existing tokens for this user.
        """
        # Invalidate all existing unused tokens for this user
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        
        # Create new token
        token = cls.objects.create(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent[:255] if user_agent else ''
        )
        return token
    
    def __str__(self):
        return f"Reset token for {self.user.username} ({'used' if self.is_used else 'active'})"
    
    class Meta:
        verbose_name = 'Password Reset Token'
        verbose_name_plural = 'Password Reset Tokens'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', 'is_used']),
        ]


class PasswordResetRateLimit(models.Model):
    """
    Rate limiting for password reset requests.
    Prevents abuse by limiting requests per email/IP.
    """
    email = models.EmailField(db_index=True)
    ip_address = models.GenericIPAddressField(db_index=True)
    request_count = models.IntegerField(default=1)
    first_request_at = models.DateTimeField(auto_now_add=True)
    last_request_at = models.DateTimeField(auto_now=True)
    
    @classmethod
    def can_request_reset(cls, email, ip_address, max_requests=3, window_minutes=60):
        """
        Check if a password reset can be requested.
        Returns (can_request: bool, wait_minutes: int)
        """
        window_start = timezone.now() - timedelta(minutes=window_minutes)
        
        # Get or create rate limit record
        rate_limit, created = cls.objects.get_or_create(
            email=email,
            ip_address=ip_address,
            defaults={'request_count': 0}
        )
        
        # Reset counter if outside window
        if rate_limit.first_request_at < window_start:
            rate_limit.request_count = 0
            rate_limit.first_request_at = timezone.now()
            rate_limit.save()
        
        # Check if limit exceeded
        if rate_limit.request_count >= max_requests:
            time_since_first = timezone.now() - rate_limit.first_request_at
            wait_minutes = max(0, window_minutes - int(time_since_first.total_seconds() / 60))
            return False, wait_minutes
        
        # Increment counter
        rate_limit.request_count += 1
        rate_limit.save()
        
        return True, 0
    
    class Meta:
        verbose_name = 'Password Reset Rate Limit'
        verbose_name_plural = 'Password Reset Rate Limits'
        unique_together = ['email', 'ip_address']
