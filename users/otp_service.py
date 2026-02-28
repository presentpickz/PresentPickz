import secrets
from django.core.mail import send_mail
from django.conf import settings
from .models import PasswordResetOTP
from django.urls import reverse

def generate_and_send_otp(user):
    # Generate 6-digit OTP
    otp_code = secrets.randbelow(900000) + 100000
    otp_code = str(otp_code)

    # Invalidate existing active OTPs for this user
    PasswordResetOTP.objects.filter(user=user, is_used=False).update(is_used=True)

    # Create new OTP record
    otp_record = PasswordResetOTP(user=user)
    otp_record.set_otp(otp_code)
    otp_record.save()
    
    # DEBUG: Print OTP to console for testing
    print(f"--------------------------------------------------")
    print(f"DEBUG OTP for {user.email}: {otp_code}")
    print(f"--------------------------------------------------")

    # Construct Reset URL (optional, or just tell them to go to the reset page)
    # We will guide them to the reset page where they enter email + OTP
    reset_url = "http://127.0.0.1:8000" + reverse('users:verify_otp')

    # Send Email
    subject = 'Password Reset Request - Access Code'
    message = f"""
    Hello {user.first_name or user.username},

    An administrator has initiated a password reset for your account.

    Your One-Time Password (OTP) is: {otp_code}

    This code is valid for 10 minutes. 
    
    Please visit the following link to reset your password:
    {reset_url}

    If you did not request this, please contact support immediately.

    Best regards,
    Present Pickz Security Team
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
    return otp_record
