from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Authentication paths
    path('', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout, name='logout'),
    
    # Password reset flow
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-code/<str:email>/', views.verify_code, name='verify_code'),
    path('reset-password/<str:email>/', views.reset_password, name='reset_password'),
    # Uncomment if using Django's built-in password reset:
    # path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),

    # Main pages
    path('homepage/', views.homepage, name='homepage'),
    path('recipe/', views.recipe, name='recipe'),
    path('recipe/<int:id>/', views.recipe_detail, name='recipe_detail'),
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('addrecipe/', views.addrecipe, name='addrecipe'),
    path('usereditrecipe/<int:recipe_id>/', views.usereditrecipe, name='usereditrecipe'),#for edting purpose of user 

    # Admin and Recipe Manager Dashboards
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('recipe_manager_dashboard/', views.recipe_manager_dashboard, name='recipe_manager_dashboard'),
    path('add_recipe/', views.add_recipe, name='add_recipe'),
    path('edit_recipe/<int:recipe_id>/', views.edit_recipe, name='edit_recipe'),
    path('delete_recipe/<int:recipe_id>/', views.delete_recipe, name='delete_recipe'),

    path('block_user/<int:user_id>/', views.block_user, name='block_user'),
    path('unblock_user/<int:user_id>/', views.unblock_user, name='unblock_user'),
    # Uncomment these if you plan to implement them:
    # path('ingredients/', views.ingredient_list, name='ingredient_list'),
    # path('nutritional-info/', views.nutritional_info_list, name='nutritional_info_list'),
] 

# Handle static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
