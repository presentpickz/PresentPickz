from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm
from django.contrib.auth.models import User
from .models import UserProfile, Address

class CustomUserCreationForm(UserCreationForm):
    # Email is crucial for ecommerce, but make optional to prevent crashes if template logic differs
    email = forms.EmailField(required=False, help_text="Optional. Add a valid email address.")

    class Meta:
        model = User
        fields = ("username", "email")

class CustomAuthenticationForm(AuthenticationForm):
    # Add Bootstrap classes for better UI
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class PasswordResetRequestForm(forms.Form):
    """Form for requesting a password reset"""
    email = forms.EmailField(
        label='Email Address',
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email',
        }),
        help_text='Enter the email address associated with your account.'
    )


class PasswordResetConfirmForm(SetPasswordForm):
    """Form for setting new password after clicking reset link"""
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password',
            'autocomplete': 'new-password',
        }),
        help_text='Your password must be at least 8 characters long.'
    )
    new_password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password',
            'autocomplete': 'new-password',
        })
    )


class UserEditForm(forms.ModelForm):
    """Form for editing user profile information"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class ProfilePhotoForm(forms.ModelForm):
    """Form for uploading profile photo"""
    class Meta:
        model = UserProfile
        fields = ['profile_photo']
        widgets = {
            'profile_photo': forms.FileInput(attrs={
                'accept': 'image/jpeg,image/png,image/jpg',
                'class': 'form-control'
            })
        }
    
    def clean_profile_photo(self):
        photo = self.cleaned_data.get('profile_photo')
        if photo:
            # Check file size (max 2MB)
            if photo.size > 2 * 1024 * 1024:
                raise forms.ValidationError('Image file too large ( > 2MB )')
            
            # Check file type
            if not photo.content_type in ['image/jpeg', 'image/png', 'image/jpg']:
                raise forms.ValidationError('Only JPG and PNG images are allowed')
        
        return photo


class AddressForm(forms.ModelForm):
    """Form for managing user addresses"""
    class Meta:
        model = Address
        fields = ['name', 'mobile', 'address_line1', 'address_line2', 'city', 'state', 'pincode', 'address_type', 'is_default']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.Select(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'address_type': forms.Select(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

