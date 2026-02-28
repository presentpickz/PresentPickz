"""
Automated Password Reset Service
Fully automated, user-controlled password reset with zero admin intervention.
"""
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.html import strip_tags
from .models import PasswordResetToken, PasswordResetRateLimit


def get_client_ip(request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """Extract user agent from request"""
    return request.META.get('HTTP_USER_AGENT', '')


def send_password_reset_email(user, token, request=None):
    """
    Send automated password reset email to user.
    No admin intervention required.
    """
    # Build reset URL
    reset_url = request.build_absolute_uri(
        reverse('users:password_reset_confirm', kwargs={'token': token.token})
    ) if request else f"http://127.0.0.1:8000{reverse('users:password_reset_confirm', kwargs={'token': token.token})}"
    
    # Email subject
    subject = 'Reset Your Password - Present Pickz'
    
    # HTML email body
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .button {{ display: inline-block; padding: 15px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; }}
            .button:hover {{ background: #764ba2; }}
            .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
            .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
            .security-info {{ background: #e7f3ff; border-left: 4px solid #2196F3; padding: 15px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 Password Reset Request</h1>
            </div>
            <div class="content">
                <p>Hello <strong>{user.first_name or user.username}</strong>,</p>
                
                <p>We received a request to reset your password for your Present Pickz account.</p>
                
                <p style="text-align: center;">
                    <a href="{reset_url}" class="button">Reset Your Password</a>
                </p>
                
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; background: #fff; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                    {reset_url}
                </p>
                
                <div class="security-info">
                    <strong>🔒 Security Information:</strong>
                    <ul>
                        <li>This link will expire in <strong>1 hour</strong></li>
                        <li>This link can only be used <strong>once</strong></li>
                        <li>Requesting a new reset will invalidate this link</li>
                    </ul>
                </div>
                
                <div class="warning">
                    <strong>⚠️ Didn't request this?</strong><br>
                    If you didn't request a password reset, please ignore this email. Your password will remain unchanged.
                    For security concerns, please contact our support team immediately.
                </div>
                
                <p>Best regards,<br>
                <strong>Present Pickz Security Team</strong></p>
            </div>
            <div class="footer">
                <p>This is an automated message. Please do not reply to this email.</p>
                <p>© 2026 Present Pickz. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version
    plain_message = f"""
    Hello {user.first_name or user.username},

    We received a request to reset your password for your Present Pickz account.

    Click the link below to reset your password:
    {reset_url}

    Security Information:
    - This link will expire in 1 hour
    - This link can only be used once
    - Requesting a new reset will invalidate this link

    Didn't request this?
    If you didn't request a password reset, please ignore this email. Your password will remain unchanged.

    Best regards,
    Present Pickz Security Team

    ---
    This is an automated message. Please do not reply to this email.
    """
    
    # Send email
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )


def initiate_password_reset(user, request):
    """
    Initiate automated password reset for a user.
    Returns (success: bool, message: str, token: PasswordResetToken or None)
    """
    # Get client info
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    # Check rate limiting
    can_request, wait_minutes = PasswordResetRateLimit.can_request_reset(
        email=user.email,
        ip_address=ip_address
    )
    
    if not can_request:
        return False, f"Too many password reset requests. Please try again in {wait_minutes} minutes.", None
    
    # Create reset token
    token = PasswordResetToken.create_for_user(
        user=user,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    # Send email
    try:
        send_password_reset_email(user, token, request)
        return True, "Password reset email sent successfully.", token
    except Exception as e:
        # Log error but don't expose details to user
        print(f"Failed to send password reset email: {e}")
        return False, "Failed to send email. Please try again later.", None
