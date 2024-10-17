from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .forms import CreateUserForm
#from .views import pending_recipes, approve_recipe, reject_recipe

urlpatterns = [
    # Authentication paths
    path('', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout, name='logout'),
    path('profile/<int:user_id>/', views.profile_view, name='profile'),
    path('edit_profile/<int:user_id>/', views.profile_edit, name='profile_edit'),
    path('edit_change/', views.profile_change, name='profile_change'),

    
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
    path('block_user/<int:user_id>/', views.block_user, name='block_user'),
    path('unblock_user/<int:user_id>/', views.unblock_user, name='unblock_user'),

    # Recipe Manager Dashboards
    path('recipe_manager_dashboard/', views.recipe_manager_dashboard, name='recipe_manager_dashboard'),
    path('add_recipe/', views.add_recipe, name='add_recipe'),
    path('edit_recipe/<int:recipe_id>/', views.edit_recipe, name='edit_recipe'),
    path('delete_recipe/<int:recipe_id>/', views.delete_recipe, name='delete_recipe'),
   # Ingredients 
    path('ingredients/', views.ingredient_list, name='ingredient_list'),
    path('ingredients/add/', views.add_ingredient, name='add_ingredient'),
    path('ingredients/edit/<int:ingredient_id>/', views.edit_ingredient, name='edit_ingredient'),
    path('ingredients/delete/<int:ingredient_id>/',views.delete_ingredient, name='delete_ingredient'),
    #nutritional_info
    path('nutritional-info/', views.nutritional_info_list, name='nutritional_info_list'),
    path('nutritional-info/add/', views.add_nutritional_info, name='add_nutritional_info'),
    path('nutritional-info/edit/<int:pk>/', views.edit_nutritional_info, name='edit_nutritional_info'),
    path('nutritional-info/delete/<int:pk>/', views.delete_nutritional_info, name='delete_nutritional_info'),
    #categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('categories/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    #support 
    path('user/contact/', views.user_contact_recipemanager, name='user_contact_recipemanager'),
    path('user/contact/success/', views.user_contact_recipemanager_success, name='user_contact_recipemanager_success'),
    path('faq/', views.faq, name='faq'),

    
   

    
    # Uncomment these if you plan to implement them:
    # path('nutritional-info/', views.nutritional_info_list, name='nutritional_info_list'),



     # Recipe interactions
    path('recipe/<int:recipe_id>/rate/', views.rate_recipe, name='rate_recipe'),
    path('recipe/<int:recipe_id>/review/', views.review_recipe, name='review_recipe'),
    path('review/<int:review_id>/comment/', views.comment_on_review, name='comment_on_review'),
    path('get-ingredients/<int:category_id>/',views.get_ingredients, name='get_ingredients'),
    #path('recipe_details/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
]


























































# Handle static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
