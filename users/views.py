from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from products.models import Product
from .models import Wishlist
from .forms import CustomUserCreationForm, CustomAuthenticationForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Security Check: Prevent Admin/Staff from logging in via frontend
                if user.is_staff or user.is_superuser:
                    logout(request)
                    messages.error(request, "Admin accounts cannot log in to the customer website.")
                    return redirect('users:login')
                
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password.")
        else:
             messages.error(request, "Invalid username or password.")
    else:
        form = CustomAuthenticationForm()

    return render(request, 'users/login.html', {'form': form})

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Explicitly specify the backend to avoid multiple backend issues
            from django.contrib.auth import get_backends
            backend = get_backends()[0]
            user.backend = f'{backend.__module__}.{backend.__class__.__name__}'
            login(request, user, backend=user.backend)
            messages.success(request, "Account created successfully! Welcome to Present Pickz.")
            return redirect('home')
        else:
             messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/signup.html', {'form': form})

def logout_view(request):
    """Handle user logout"""
    if request.method == 'POST' or request.method == 'GET':
        logout(request)
        messages.info(request, "You have been logged out.")
        return redirect('home')
    return redirect('home')

def wishlist_view(request):
    """Display the user's wishlist"""
    wishlist_items = []
    
    if request.user.is_authenticated:
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        wishlist_items = wishlist.products.all()
    else:
        # Session based
        wishlist_ids = request.session.get('wishlist', [])
        wishlist_items = Product.objects.filter(id__in=wishlist_ids)
        
    return render(request, 'users/wishlist.html', {'products': wishlist_items})

def toggle_wishlist(request, product_id):
    """Add or remove item from wishlist"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.user.is_authenticated:
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        if wishlist.products.filter(id=product_id).exists():
            wishlist.products.remove(product)
            added = False
        else:
            wishlist.products.add(product)
            added = True
    else:
        # Session based
        if 'wishlist' not in request.session:
            request.session['wishlist'] = []
            
        wishlist_ids = request.session['wishlist']
        if product_id in wishlist_ids:
            wishlist_ids.remove(product_id)
            added = False
        else:
            wishlist_ids.append(product_id)
            added = True
        request.session.modified = True
            
    # Return JSON if AJAX otherwise redirect
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'added': added, 'count': get_wishlist_count(request)})
        
    # Redirect back to where they came from
    next_url = request.META.get('HTTP_REFERER', 'products:product_list')
    return redirect(next_url)

def get_wishlist_count(request):
    if request.user.is_authenticated:
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        return wishlist.products.count()
    else:
        return len(request.session.get('wishlist', []))

@login_required
def account_dashboard(request):
    """User account dashboard with profile overview"""
    from orders.models import Order
    from users.models import Wishlist, Address
    from products.models import Review
    
    # Get counts
    total_orders = Order.objects.filter(user=request.user).count()
    wishlist_count = 0
    if hasattr(request.user, 'wishlist'):
        wishlist_count = request.user.wishlist.products.count()
        
    address_count = Address.objects.filter(user=request.user).count()
    review_count = Review.objects.filter(user=request.user).count()
    
    context = {
        'user': request.user,
        'active_tab': 'dashboard',
        'total_orders': total_orders,
        'wishlist_count': wishlist_count,
        'address_count': address_count,
        'review_count': review_count,
    }
    return render(request, 'users/account/dashboard.html', context)

@login_required
def saved_addresses(request):
    """Manage saved addresses"""
    from users.models import Address
    addresses = Address.objects.filter(user=request.user)
    context = {
        'addresses': addresses,
        'active_tab': 'addresses'
    }
    return render(request, 'users/account/saved_addresses.html', context)

@login_required
def add_address(request):
    from .forms import AddressForm
    
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            addr = form.save(commit=False)
            addr.user = request.user
            addr.save()
            messages.success(request, "Address added successfully")
            return redirect('users:saved_addresses')
    else:
        form = AddressForm()
    
    return render(request, 'users/account/address_form.html', {'form': form, 'title': 'Add New Address'})

@login_required
def edit_address(request, address_id):
    from .forms import AddressForm
    from users.models import Address
    
    addr = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=addr)
        if form.is_valid():
            form.save()
            messages.success(request, "Address updated successfully")
            return redirect('users:saved_addresses')
    else:
        form = AddressForm(instance=addr)
    
    return render(request, 'users/account/address_form.html', {'form': form, 'title': 'Edit Address'})

@login_required
def delete_address(request, address_id):
    from users.models import Address
    addr = get_object_or_404(Address, id=address_id, user=request.user)
    addr.delete()
    messages.success(request, "Address deleted successfully")
    return redirect('users:saved_addresses')

@login_required
@ensure_csrf_cookie
def edit_profile(request):
    from .forms import UserEditForm, ProfilePhotoForm
    from .models import UserProfile
    
    # Ensure user has a profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully")
            return redirect('users:account')
    else:
        form = UserEditForm(instance=request.user)
    
    photo_form = ProfilePhotoForm()
    
    context = {
        'form': form,
        'photo_form': photo_form,
        'active_tab': 'profile',
        'profile': profile
    }
    return render(request, 'users/account/edit_profile.html', context)

@login_required
@require_http_methods(["POST"])
def upload_profile_photo(request):
    """Handle profile photo upload via AJAX"""
    from .forms import ProfilePhotoForm
    from .models import UserProfile
    
    if request.method == 'POST':
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        form = ProfilePhotoForm(request.POST, request.FILES)
        
        if form.is_valid():
            photo = form.cleaned_data.get('profile_photo')
            if photo:
                # Delete old photo if exists
                if profile.profile_photo:
                    profile.delete_photo()
                
                # Save new photo
                profile.profile_photo = photo
                profile.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Profile photo updated successfully',
                    'photo_url': profile.profile_photo.url
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'No photo provided'
                }, status=400)
        else:
            errors = form.errors.get('profile_photo', ['Invalid file'])
            return JsonResponse({
                'success': False,
                'message': errors[0]
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

@login_required
def delete_profile_photo(request):
    """Delete profile photo"""
    from .models import UserProfile
    
    if request.method == 'POST':
        try:
            profile = UserProfile.objects.get(user=request.user)
            profile.delete_photo()
            
            return JsonResponse({
                'success': True,
                'message': 'Profile photo removed successfully'
            })
        except UserProfile.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Profile not found'
            }, status=404)
    
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

@login_required
def debug_profile(request):
    """Debug page to check profile photo status"""
    return render(request, 'users/debug_profile.html')



@login_required
def my_reviews(request):
    from products.models import Review
    reviews = Review.objects.filter(user=request.user)
    return render(request, 'users/account/my_reviews.html', {'reviews': reviews, 'active_tab': 'reviews'})

from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'users/account/password_change.html'
    success_url = reverse_lazy('users:account')
    
    def form_valid(self, form):
        messages.success(self.request, "Your password has been changed successfully!")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'profile'
        return context


def password_reset_request(request):
    """
    FULLY AUTOMATED PASSWORD RESET - Step 1: Request Reset
    User enters email, system sends reset link automatically.
    NO admin intervention required.
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        from .forms import PasswordResetRequestForm
        from .password_reset_service import initiate_password_reset
        
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # Find user by email (case-insensitive)
            user = User.objects.filter(email__iexact=email).first()
            
            if user:
                # Initiate password reset
                success, message, token = initiate_password_reset(user, request)
                
                if success:
                    messages.success(
                        request,
                        "Password reset email sent! Please check your inbox and spam folder."
                    )
                    return redirect('users:password_reset_sent')
                else:
                    messages.error(request, message)
            else:
                # Don't reveal if email exists (security best practice)
                # Show success message anyway to prevent email enumeration
                messages.success(
                    request,
                    "If an account exists with this email, you will receive a password reset link shortly."
                )
                return redirect('users:password_reset_sent')
    else:
        from .forms import PasswordResetRequestForm
        form = PasswordResetRequestForm()
    
    return render(request, 'users/password_reset_request.html', {'form': form})


def password_reset_sent(request):
    """Confirmation page after password reset email is sent"""
    return render(request, 'users/password_reset_sent.html')


def password_reset_confirm(request, token):
    """
    FULLY AUTOMATED PASSWORD RESET - Step 2: Confirm Reset
    User clicks link in email, validates token, sets new password.
    NO admin intervention required.
    """
    from .models import PasswordResetToken
    from .forms import PasswordResetConfirmForm
    
    # Validate token
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
    except PasswordResetToken.DoesNotExist:
        messages.error(request, "Invalid password reset link.")
        return redirect('users:password_reset_request')
    
    # Check if token is valid
    if not reset_token.is_valid():
        if reset_token.is_used:
            messages.error(request, "This password reset link has already been used.")
        else:
            messages.error(request, "This password reset link has expired. Please request a new one.")
        return redirect('users:password_reset_request')
    
    # Process password reset
    if request.method == 'POST':
        form = PasswordResetConfirmForm(reset_token.user, request.POST)
        if form.is_valid():
            # Set new password
            user = reset_token.user
            user.set_password(form.cleaned_data['new_password1'])
            user.save()
            
            # Mark token as used
            reset_token.mark_as_used()
            
            # Invalidate all sessions for this user (force re-login)
            from django.contrib.sessions.models import Session
            from django.utils import timezone
            for session in Session.objects.filter(expire_date__gte=timezone.now()):
                session_data = session.get_decoded()
                if session_data.get('_auth_user_id') == str(user.id):
                    session.delete()
            
            messages.success(
                request,
                "Password reset successful! You can now log in with your new password."
            )
            return redirect('users:password_reset_complete')
    else:
        form = PasswordResetConfirmForm(reset_token.user)
    
    context = {
        'form': form,
        'token': token,
        'user_email': reset_token.user.email
    }
    return render(request, 'users/password_reset_confirm.html', context)


def password_reset_complete(request):
    """Success page after password reset is complete"""
    return render(request, 'users/password_reset_complete.html')

