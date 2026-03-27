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

from django import forms

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={'multiple': True}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result

class ProductAdminForm(forms.ModelForm):
    gallery_images = MultipleFileField(
        label='Upload Multiple Gallery Images',
        required=False,
        help_text='Select multiple images at once to upload them to this product\'s gallery.'
    )

    class Meta:
        model = Product
        fields = '__all__'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ['name', 'price', 'original_price', 'category', 'is_new', 'is_bestseller', 'stock']
    list_editable = ['price', 'stock', 'is_new', 'is_bestseller']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['category', 'is_new', 'is_bestseller']
    inlines = [ProductImageInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        # Handle multiple images upload
        if request.FILES.getlist('gallery_images'):
            for f in request.FILES.getlist('gallery_images'):
                ProductImage.objects.create(product=obj, image=f)

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
