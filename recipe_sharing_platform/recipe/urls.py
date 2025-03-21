from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
# from .forms import CreateUserForm
#from .views import pending_recipes, approve_recipe, reject_recipe

# Remove the app_name to resolve the namespace issue
# app_name = 'recipe'

urlpatterns = [
    # Authentication paths
    path('', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/change/', views.profile_change, name='profile_change'),

    
    # Password reset flow
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-code/<str:email>/', views.verify_code, name='verify_code'),
    path('reset-password/<str:email>/', views.reset_password, name='reset_password'),
    # Uncomment if using Django's built-in password reset:
    # path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),

    # Main pages
    path('homepage/', views.homepage, name='homepage'),
    path('recipe/', views.recipe, name='recipe'),
    path('recipe/<int:recipe_id>/edit/', views.usereditrecipe, name='usereditrecipe'),
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('addrecipe/', views.addrecipe, name='addrecipe'),
    path('search/', views.search_recipe, name='search_recipe'),
    

    # Admin 
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add-user/', views.add_user, name='add_user'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('block-user/<int:user_id>/', views.block_user, name='block_user'),
    path('unblock-user/<int:user_id>/', views.unblock_user, name='unblock_user'),
    # Admin Dashboard Recipe Management URLs
    path('add_recipe/', views.add_recipe, name='add_recipe'),
    path('edit_recipe/<int:recipe_id>/', views.edit_recipe, name='edit_recipe'),
    path('delete_recipe/<int:recipe_id>/', views.delete_recipe, name='delete_recipe'),

    # Ingredients URLs
    path('ingredients/', views.ingredient_list, name='ingredient_list'),
    path('ingredients/add/', views.add_ingredient, name='add_ingredient'),
    path('ingredients/edit/<int:ingredient_id>/', views.edit_ingredient, name='edit_ingredient'),
    path('ingredients/delete/<int:ingredient_id>/', views.delete_ingredient, name='delete_ingredient'),

    # Nutritional Info URLs
    path('nutritional-info/', views.nutritional_info_list, name='nutritional_info_list'),
    path('recipe/<int:recipe_id>/nutritional-info/', views.add_edit_nutritional_info, name='add_edit_nutritional_info'),
    path('recipe/<int:recipe_id>/delete-nutritional-info/', views.delete_nutritional_info, name='delete_nutritional_info'),

    # Categories URLs
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('categories/disable/<int:category_id>/', views.delete_category, name='delete_category'),
    path('categories/enable/<int:category_id>/', views.enable_category, name='enable_category'),

    #support 
    path('user/contact/', views.user_contact_recipemanager, name='user_contact_recipemanager'),
    path('user/contact/success/', views.user_contact_recipemanager_success, name='user_contact_recipemanager_success'),
    # path('faq/', views.faq, name='faq'),

    # Manage Users
    path('manage_users/', views.manage_users, name='manage_users'),
    path('manage_subcategories/', views.manage_subcategories, name='manage_subcategories'),
    path('manage_events/', views.manage_events, name='manage_events'),

   #manage subcategories
    path('subcategories/', views.subcategory_list, name='subcategory_list'),
    path('subcategories/add/', views.add_subcategory, name='add_subcategory'),
    path('subcategories/edit/<int:subcategory_id>/', views.edit_subcategory, name='edit_subcategory'),
    path('subcategories/delete/<int:subcategory_id>/', views.delete_subcategory, name='delete_subcategory'),
    
    # Uncomment these if you plan to implement them:
    # path('nutritional-info/', views.nutritional_info_list, name='nutritional_info_list'),

   path('get-subcategories/<int:category_id>/', views.get_subcategories, name='get_subcategories'),
     # Recipe interactions
    path('recipe/<int:recipe_id>/rate/', views.rate_recipe, name='rate_recipe'),
    path('recipe/<int:recipe_id>/review/', views.review_recipe, name='review_recipe'),
    path('review/<int:review_id>/comment/', views.comment_on_review, name='comment_on_review'),
    path('get-ingredients/<int:category_id>/', views.get_ingredients, name='get_ingredients'),

    
  path('subcategories/add/', views.add_subcategory, name='add_subcategory'),
  
    # ... other URLs ...
    #path('recipe_details/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('api/search-suggestions/', views.search_suggestions, name='search_suggestions'),
    path('workshop/', views.workshop_view, name='workshop'),
    path('baking/', views.baking_view, name='baking'),
    path('food-photography/', views.food_photography_view, name='food_photography'),
   
    path('api/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    
    path('events/create/', views.create_event, name='create_event'),
    path('events/my-events/', views.my_events, name='my_events'),
    path('events/view/', views.view_events, name='view_events'),
    path('event/registration/<int:event_id>/', views.event_registration, name='event_registration'),
    path('events/edit/<int:event_id>/', views.edit_event, name='edit_event'),
    path('events/delete/<int:event_id>/', views.delete_event, name='delete_event'),




    path('meal-planner/', views.meal_planner, name='meal_planner'),
    path('add-meal/', views.add_meal_plan, name='add_meal_plan'),
    path('meal-planner/edit/<int:meal_id>/', views.edit_meal, name='edit_meal'),
    path('meal-planner/delete/<int:meal_id>/', views.delete_meal_plan, name='delete_meal'),
    
    path('recipe/<int:recipe_id>/analyze-diet/', views.analyze_recipe_diet, name='analyze_recipe_diet'),
    
    path('recipe/<int:recipe_id>/delete/', views.delete_user_recipe, name='delete_recipe'),

    # Add these new URL patterns
    path('subscription/plans/', views.subscription_plans, name='subscription_plans'),
    path('subscription/checkout/<int:plan_id>/', views.subscription_checkout, name='subscription_checkout'),
    path('subscription/process/<int:plan_id>/', views.process_subscription, name='process_subscription'),
    path('subscription/success/', views.subscription_success, name='subscription_success'),
    path('subscription/cancel/', views.subscription_cancel, name='subscription_cancel'),
    path('subscription/webhook/', views.razorpay_webhook, name='razorpay_webhook'),
    path('subscription/status/', views.subscription_status, name='subscription_status'),
]



# Handle static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
