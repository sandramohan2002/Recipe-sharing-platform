from django.db import migrations
from django.utils import timezone

def create_initial_subscription_plans(apps, schema_editor):
    SubscriptionPlan = apps.get_model('recipe', 'SubscriptionPlan')
    
    # Create Basic Premium Plan
    SubscriptionPlan.objects.create(
        name='Basic Premium',
        description='Get started with premium features',
        price=499.00,
        duration='monthly',
        features=[
            'Access to premium recipes',
            'Basic meal planning',
            'Ad-free experience',
            'Priority support'
        ],
        is_active=True,
        created_at=timezone.now(),
        updated_at=timezone.now()
    )

    # Create Premium Plus Plan
    SubscriptionPlan.objects.create(
        name='Premium Plus',
        description='Full access to all premium features',
        price=4999.00,
        duration='yearly',
        features=[
            'All Basic Premium features',
            'Advanced recipe analytics',
            'Personalized meal plans',
            'Recipe download feature',
            'Nutritional insights',
            'Early access to new features'
        ],
        is_active=True,
        created_at=timezone.now(),
        updated_at=timezone.now()
    )

    # Create Pro Chef Plan
    SubscriptionPlan.objects.create(
        name='Pro Chef',
        description='Professional features for serious cooks',
        price=999.00,
        duration='monthly',
        features=[
            'All Basic Premium features',
            'Professional recipe scaling',
            'Advanced cooking techniques',
            'Private cooking consultations',
            'Recipe cost calculator',
            'Inventory management',
            'Commercial kitchen adaptations'
        ],
        is_active=True,
        created_at=timezone.now(),
        updated_at=timezone.now()
    )

def remove_subscription_plans(apps, schema_editor):
    SubscriptionPlan = apps.get_model('recipe', 'SubscriptionPlan')
    SubscriptionPlan.objects.filter(name__in=[
        'Basic Premium',
        'Premium Plus',
        'Pro Chef'
    ]).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('recipe', '0006_paymenthistory_subscriptionplan_usersubscription'),
    ]

    operations = [
        migrations.RunPython(
            create_initial_subscription_plans,
            remove_subscription_plans
        ),
    ] 