from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.utils import generate_unique_username
from django.contrib.auth import get_user_model

User = get_user_model()

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_auto_signup_allowed(self, request, sociallogin):
        """
        ALWAYS allow auto signup - NEVER show the signup form
        """
        return True
    
    def populate_user(self, request, sociallogin, data):
        """
        Populate user with a valid username to avoid signup form.
        """
        user = super().populate_user(request, sociallogin, data)
        
        # If user is already set (e.g. connected to existing account), skip
        if user.pk:
            return user
            
        # ALWAYS ensure username is set
        if not user.username:
            username_candidates = []
            
            # 1. Try email prefix
            email = data.get('email')
            if email:
                username_candidates.append(email.split('@')[0])
            
            # 2. Try various name combinations
            name = data.get('name')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            
            if name:
                username_candidates.append(name.replace(' ', '').lower())
            if first_name:
                username_candidates.append(first_name.lower())
            if last_name:
                username_candidates.append(last_name.lower())
            if first_name and last_name:
                username_candidates.append(f"{first_name}{last_name}".lower())
                
            # 3. Fallback to Google ID
            if sociallogin.account.uid:
                username_candidates.append(f"user{sociallogin.account.uid}")
                
            # 4. Final fallback
            username_candidates.append('user')
            
            # Filter and generate
            valid_candidates = [u for u in username_candidates if u]
            user.username = generate_unique_username(valid_candidates)
            
        return user

    def save_user(self, request, sociallogin, form=None):
        """
        Save user without requiring form
        """
        user = sociallogin.user
        user.set_unusable_password()
        
        # Ensure username is ALWAYS set
        if not user.username:
            self.populate_user(request, sociallogin, sociallogin.account.extra_data)
             
        user.save()
        sociallogin.save(request)
        return user
        
    def pre_social_login(self, request, sociallogin):
        """
        Connect existing user if email matches
        """
        if sociallogin.is_existing:
            return
            
        try:
            email = sociallogin.account.extra_data.get('email')
            if email:
                user = User.objects.get(email=email)
                sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass
