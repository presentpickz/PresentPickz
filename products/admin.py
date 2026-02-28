from django.contrib import admin
from .models import Category, Product, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_featured']
    list_editable = ['is_featured']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'original_price', 'category', 'is_new', 'is_bestseller', 'stock']
    list_editable = ['price', 'stock', 'is_new', 'is_bestseller']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['category', 'is_new', 'is_bestseller']
    inlines = [ProductImageInline]

from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at', 'is_hidden']
    list_filter = ['rating', 'is_hidden', 'created_at']
    search_fields = ['product__name', 'user__username', 'comment']
    list_editable = ['is_hidden']
    
    # Security: Reviews are user-generated content
    # Admin cannot modify rating or create reviews manually
    readonly_fields = ['user', 'product', 'order', 'rating', 'created_at']
    
    def has_add_permission(self, request):
        return False
