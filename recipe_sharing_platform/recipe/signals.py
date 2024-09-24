# signals.py
from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from .models import CustomUser

@receiver(user_signed_up)
def create_custom_user(sender, request, user, **kwargs):
    # Extract the user's social account data
    social_account = user.socialaccount_set.filter(provider='google').first()
    
    if social_account:
        user_data = social_account.extra_data
        email = user.email
        name = user_data.get('name')

        # Save the user's details in the CustomUser table
        custom_user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults={'name': name, 'password': user.password}
        )
        if not created:
            custom_user.name = name  # Update the name if it exists
            custom_user.save()
