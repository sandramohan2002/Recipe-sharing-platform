import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from .models import CustomUser, SubCategory, Recipe, NutritionalInformation, Ingredient, Category, Rating, Review, Comment, RecipeIngredient, EventRegistration, Favorite, RecipeAllergen, Event, MealPlan, DietaryTracking, DietaryGuideline
from .forms import RecipeForm, NutritionalInformationForm, ProfileForm, IngredientForm, CategoryForm, CreateUserForm, ContactForm, SubCategoryForm
from django.db.models import Q, Avg
from django.core.mail import send_mail 
import logging
# from django.urls import reverse
from django.db import transaction
# from django.conf import settings
import traceback
from django.http import JsonResponse
import re
from datetime import datetime, timedelta
from django.utils import timezone
from .image_classifier import RecipeImageClassifier
from django.conf import settings
from .ai_utils import get_nutritional_info_from_ai
from django.db.models import Count
from django.views.decorators.http import require_http_methods
import json


logger = logging.getLogger(__name__)

#USER DASHBOARD
def signup(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            email = request.POST.get('email')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            # Get optional fields
            age = request.POST.get('age')
            mobile = request.POST.get('mobile')
            date_of_birth = request.POST.get('date_of_birth')
            diet_preference = request.POST.get('diet_preference')
            profile_image = request.FILES.get('profile_image')

            if password1 != password2:
                messages.error(request, 'Passwords do not match')
                return redirect('signup')

            # Create user with all provided information
            user = CustomUser(
                name=name,
                email=email,
                password=password1,
                age=age if age else None,
                mobile=mobile if mobile else None,
                date_of_birth=date_of_birth if date_of_birth else None,
                diet_preference=diet_preference if diet_preference != 'other' else None,
                profile_image=profile_image if profile_image else None
            )
            user.save()

            messages.success(request, 'Account created successfully')
            return redirect('login')
            
        except IntegrityError:
            messages.error(request, 'Email already exists')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            
    return render(request, 'signup.html')


def login(request):
    if request.method == 'POST':
        email = request.POST.get('Email')
        password = request.POST.get('password')

        if not email or not password:
            return render(request, 'login.html', {'error': 'Email and password are required'})

        try:
            user = CustomUser.objects.get(email=email)
            
            # Check if it's the admin user
            if user.email == "admin@gmail.com" and user.password == "Admin@123":
                request.session['id'] = user.id
                request.session['is_admin'] = True
                request.session['username'] = user.name
                request.session['email'] = user.email
                return redirect('admin_dashboard')
            else:
                # For regular users, directly compare plain text passwords
                if user.password == password:
                    request.session['id'] = user.id
                    request.session['is_admin'] = False  # Assuming regular users are not admins
                    request.session['username'] = user.name
                    request.session['email'] = user.email
                    return redirect('homepage')
                else:
                    return render(request, 'login.html', {'error': 'Incorrect password'})
                
        except CustomUser.DoesNotExist:
            return render(request, 'login.html', {'error': 'Email does not exist'})
    
    return render(request, 'login.html')
user_pins = {}

# Forgot password view
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            code = random.randint(1000, 9999)# Generate a random 4-digit code
            user_pins[email] = code # Send email with the code  
            send_mail(
                'Password Reset Code',
                f'Your password reset code is {code}.',
                'admin@yourdomain.com',  # Change to your domain
                [email],
                fail_silently=False,
            )
            # Redirect to the verification page
            return redirect('verify_code', email=email)
        except User.DoesNotExist:
            messages.error(request, 'Invalid email address.')
    return render(request, 'forgot_password.html')


# Verify code view
def verify_code(request, email):
    if request.method == 'POST':
        entered_code = request.POST.get('pin')
        correct_code = user_pins.get(email)

        if correct_code and str(entered_code) == str(correct_code):
            # Redirect to reset password page
            return redirect('reset_password', email=email)
        else:
            messages.error(request, 'Invalid code. Please try again.')

    return render(request, 'verifycode.html',{'email': email})


# Reset password view
def reset_password(request, email):
    if request.method == 'POST':
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if new_password1 == new_password2:
            try:
                user = CustomUser.objects.get(email=email)
                user.password = new_password1  # Directly set the password
                user.save()  # Save the changes to the database
                messages.success(request, 'Password has been reset successfully.')
                return redirect('login')
            except CustomUser.DoesNotExist:
                messages.error(request, 'Invalid user.')
        else:
            messages.error(request, 'Passwords do not match.')
    return render(request, 'resetpassword.html',{'email': email})


def logout(request):
    #auth_logout(request) 
    request.session.flush()
    return redirect('login')







#HOMEPAGE VIEW
def homepage(request):
    # Get current date
    current_date = timezone.now().date()
    
    # Get featured events (all upcoming events with images)
    featured_events = Event.objects.filter(
        event_date__gte=current_date,
        status='upcoming',
        image__isnull=False
    ).order_by('event_date', 'event_time')[:6]  # Show up to 6 featured events
    
    context = {
        'featured_events': featured_events,
        'guest_message': "Welcome, Guest! Please log in or sign up.",
    }
    return render(request, 'homepage.html', context)

def search_recipe(request):
    query = request.GET.get('query', '')
    if query:
        try:
            recipe = Recipe.objects.get(recipename__iexact=query) # Perform a case-insensitive search for the recipe
            return redirect('recipe_detail', recipe_id=recipe.recipe_id)
        except Recipe.DoesNotExist:
            return redirect('homepage')# Redirect to homepage or show a "not found" message if the recipe doesn't exist
    return redirect('homepage')
logger = logging.getLogger(__name__)

def recipe(request):
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    selected_category = request.GET.get('category_id', '')
    selected_subcategory = request.GET.get('subcategory_id', '')
    search_query = request.GET.get('search', '')
    show_my_recipes = request.GET.get('my_recipes', '') == 'true'
    
    current_user_id = request.session.get('id')
    favorite_recipes = []
    if current_user_id:
        favorite_recipes = Favorite.objects.filter(user_id=current_user_id).values_list('recipe_id', flat=True)
    
    recipes = Recipe.objects.all()
    
    if show_my_recipes:
        if current_user_id:
            recipes = recipes.filter(user_id=current_user_id)
        else:
            recipes = Recipe.objects.none()  # Return an empty queryset if user is not logged in
    
    if selected_category:
        try:
            selected_category = int(selected_category)
            recipes = recipes.filter(category_id=selected_category)
        except (ValueError, TypeError):
            logger.warning(f"Invalid category_id: {selected_category}")
    
    if selected_subcategory:
        try:
            selected_subcategory = int(selected_subcategory)
            recipes = recipes.filter(subcategory_id=selected_subcategory)
        except (ValueError, TypeError):
            logger.warning(f"Invalid subcategory_id: {selected_subcategory}")
    
    if search_query:
        recipes = recipes.filter(Q(recipename__icontains=search_query) | Q(tags__icontains=search_query))
    
    for recipe in recipes:
        recipe.can_edit = (recipe.user_id == current_user_id)
    
    logger.debug(f"Total recipes: {recipes.count()}")
    logger.debug(f"Show my recipes: {show_my_recipes}")
    logger.debug(f"Current user ID: {current_user_id}")
    
    for recipe in recipes:
        logger.info(f"Recipe ID: {recipe.recipe_id}, Recipe ID type: {type(recipe.recipe_id)}, Name: {recipe.recipename}")
    
    context = {
        'categories': categories,
        'subcategories': subcategories,
        'recipes': recipes,
        'selected_category': selected_category,
        'selected_subcategory': selected_subcategory,
        'current_user_id': current_user_id,
        'show_my_recipes': show_my_recipes,
        'search_query': search_query,
        'favorite_recipes': favorite_recipes,
    }
    
    return render(request, 'recipe.html', context)


#ABOUT VIEW
def about(request):
    return render(request, 'about.html' )



def contact(request):
    return render(request, 'contact.html')


from django.db import transaction


@transaction.atomic
def addrecipe(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Create recipe with basic info
                recipe = Recipe.objects.create(
                    user_id=request.session.get('id'),
                    recipename=request.POST.get('recipename'),
                    category_id=request.POST.get('category'),
                    subcategory_id=request.POST.get('subcategory') or None,
                    tags=request.POST.get('tags', ''),
                    servings=request.POST.get('servings') or 1,
                    prep_time=request.POST.get('prep_time') or 0,
                    cook_time=request.POST.get('cook_time') or 0,
                    difficulty=request.POST.get('difficulty', 'medium')
                )

                # Handle image
                if 'image' in request.FILES:
                    recipe.image = request.FILES['image']
                    recipe.save()

                # Handle ingredients
                ingredient_count = int(request.POST.get('ingredient_count', 0))
                for i in range(1, ingredient_count + 1):
                    ingredient_id = request.POST.get(f'ingredient_id_{i}')
                    quantity = request.POST.get(f'quantity_{i}')
                    measurement = request.POST.get(f'measurement_{i}')

                    if ingredient_id and quantity and measurement:
                        RecipeIngredient.objects.create(
                            recipe=recipe,
                            ingredient_id=ingredient_id,
                            quantity=float(quantity),
                            measurement=measurement
                        )

                # Handle instructions
                instructions = []
                for key in request.POST:
                    if key.startswith('instruction_step_'):
                        step = request.POST.get(key)
                        if step.strip():
                            instructions.append(step.strip())
                
                # Save instructions as a single string with newlines
                recipe.instructions = '\n'.join(instructions)
                recipe.save()

                # Handle allergens
                allergen_names = request.POST.getlist('allergen_name[]')
                severities = request.POST.getlist('severity[]')
                notes = request.POST.getlist('allergen_notes[]')

                for name, severity, note in zip(allergen_names, severities, notes):
                    if name and severity:
                        RecipeAllergen.objects.create(
                            recipe=recipe,
                            allergen_name=name,
                            severity=severity,
                            notes=note or ''
                        )

                messages.success(request, 'Recipe added successfully!')
                return redirect('recipe_detail', recipe.recipe_id)

        except Exception as e:
            print(f"Error in addrecipe: {str(e)}")
            messages.error(request, f'Error adding recipe: {str(e)}')
            return render(request, 'addrecipe.html', {
                'categories': Category.objects.all(),
                'ingredients': Ingredient.objects.all(),
                'error': str(e)
            })

    return render(request, 'addrecipe.html', {
        'categories': Category.objects.all(),
        'ingredients': Ingredient.objects.all()
    })



def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, recipe_id=recipe_id)
    
    # Get nutritional info
    try:
        nutritional_info = NutritionalInformation.objects.get(recipe_id=recipe_id)
        is_ai_generated = nutritional_info.is_ai_generated
    except NutritionalInformation.DoesNotExist:
        nutritional_info = None
        is_ai_generated = False
        
        # Try to generate nutritional info if it doesn't exist
        try:
            api_key = getattr(settings, 'GEMINI_API_KEY', None)
            if api_key:
                ai_nutritional_info = get_nutritional_info_from_ai(recipe.recipename, api_key)
                if ai_nutritional_info:
                    nutritional_info = NutritionalInformation.objects.create(
                        recipe=recipe,
                        calories=ai_nutritional_info['calories'],
                        protein=ai_nutritional_info['protein'],
                        carbohydrates=ai_nutritional_info['carbohydrates'],
                        fat=ai_nutritional_info['fat'],
                        fiber=ai_nutritional_info['fiber'],
                        sugar=ai_nutritional_info['sugar'],
                        is_ai_generated=True
                    )
                    is_ai_generated = True
            else:
                print("No Gemini API key found in settings")
        except Exception as e:
            print(f"Error generating nutritional info: {str(e)}")
            pass  # Handle error silently

    # Get the recipe author details
    try:
        recipe_author = CustomUser.objects.get(id=recipe.user_id)
        author_name = recipe_author.name
        author_profile_image = recipe_author.profile_image
    except CustomUser.DoesNotExist:
        author_name = "Unknown User"
        author_profile_image = None
    
    # Get the user_id from request.session
    user_id = request.session.get('id')
    is_logged_in = user_id is not None
    
    # Get reviews
    try:
        reviews = Review.objects.filter(recipe_id=recipe_id).values(
            'review_id', 'user_id', 'review_text', 'created_at'
        ).order_by('-created_at')
        
        # Fetch user names for reviews
        for review in reviews:
            try:
                user = CustomUser.objects.get(id=review['user_id'])
                review['user_name'] = user.name
            except CustomUser.DoesNotExist:
                review['user_name'] = "Unknown User"
    except:
        reviews = []

    # Get category and subcategory
    try:
        category = Category.objects.get(category_id=recipe.category_id)
        category_name = category.name
    except Category.DoesNotExist:
        category_name = "Unknown Category"
    
    try:
        subcategory = SubCategory.objects.get(subcategory_id=recipe.subcategory_id)
        subcategory_name = subcategory.name
    except SubCategory.DoesNotExist:
        subcategory_name = "Unknown Subcategory"

    # Get ingredients
    ingredients = recipe.recipe_ingredients.all().select_related('ingredient')

    # Split instructions into a list
    instructions = [inst.strip() for inst in recipe.instructions.split('\n') if inst.strip()]

    # Fetch allergens and organize them by severity
    allergens = {
        'contains': [],
        'may_contain': [],
        'traces': []
    }
    
    recipe_allergens = RecipeAllergen.objects.filter(recipe_id=recipe_id)
    for allergen in recipe_allergens:
        allergen_info = {
            'name': allergen.get_allergen_name_display(),
            'notes': allergen.notes
        }
        allergens[allergen.severity].append(allergen_info)

    # Check if user is admin
    is_admin = request.user.is_admin if hasattr(request.user, 'is_admin') else False

    context = {
        'recipe': recipe,
        'author_name': author_name,
        'author_profile_image': author_profile_image,
        'category_name': category_name,
        'subcategory_name': subcategory_name,
        'instructions': instructions,
        'nutritional_info': nutritional_info,
        'ingredients': ingredients,
        'allergens': allergens,
        'has_allergens': any(allergens.values()),
        'reviews': reviews,
        'reviews_display': True,
        'is_admin': is_admin,
        'is_logged_in': is_logged_in,
        'user_id': user_id,
        'messages': messages.get_messages(request),
        'is_ai_generated': is_ai_generated,
    }
    
    return render(request, 'recipe_detail.html', context)

#for edting recipes on recipe page for user
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import RecipeForm
import logging
from .models import Recipe, RecipeIngredient, Ingredient, Category
import logging
from django.db import transaction


logger = logging.getLogger(__name__)

def usereditrecipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, recipe_id=recipe_id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Update recipe basic info
                recipe.recipename = request.POST.get('recipename')
                recipe.category_id = request.POST.get('category')
                recipe.subcategory_id = request.POST.get('subcategory')
                recipe.servings = request.POST.get('servings')
                recipe.prep_time = request.POST.get('prep_time')
                recipe.cook_time = request.POST.get('cook_time')
                recipe.difficulty = request.POST.get('difficulty')
                recipe.instructions = '\n'.join(request.POST.getlist('instructions[]'))
                
                if 'image' in request.FILES:
                    recipe.image = request.FILES['image']
                
                recipe.save()

                # Update recipe ingredients
                RecipeIngredient.objects.filter(recipe=recipe).delete()
                ingredient_ids = request.POST.getlist('ingredient[]')
                quantities = request.POST.getlist('quantity[]')
                measurements = request.POST.getlist('measurement[]')

                for i in range(len(ingredient_ids)):
                    ingredient = get_object_or_404(Ingredient, ingredient_id=ingredient_ids[i])
                    RecipeIngredient.objects.create(
                        recipe=recipe,
                        ingredient=ingredient,
                        quantity=quantities[i],
                        measurement=measurements[i]
                    )

                # Update allergens
                # First, delete existing allergens
                RecipeAllergen.objects.filter(recipe_id=recipe_id).delete()
                
                # Add new allergens
                allergen_names = request.POST.getlist('allergen_name[]')
                allergen_severities = request.POST.getlist('allergen_severity[]')
                allergen_notes = request.POST.getlist('allergen_notes[]')
                
                for i in range(len(allergen_names)):
                    if allergen_names[i] and allergen_severities[i]:
                        RecipeAllergen.objects.create(
                            recipe_id=recipe_id,
                            allergen_name=allergen_names[i],
                            severity=allergen_severities[i],
                            notes=allergen_notes[i] if allergen_notes[i] else None
                        )

                messages.success(request, 'Recipe updated successfully!')
                return redirect('recipe_detail', recipe_id=recipe_id)
            
        except Exception as e:
            messages.error(request, f'Error updating recipe: {str(e)}')
    
    # Get data for the form
    categories = Category.objects.all()
    subcategories = SubCategory.objects.filter(category_id=recipe.category_id)
    ingredients = Ingredient.objects.all()
    recipe_ingredients = RecipeIngredient.objects.filter(recipe_id=recipe_id)
    recipe_allergens = RecipeAllergen.objects.filter(recipe_id=recipe_id)
    instructions = recipe.instructions.split('\n') if recipe.instructions else []
    
    context = {
        'recipe': recipe,
        'categories': categories,
        'subcategories': subcategories,
        'ingredients': ingredients,
        'recipe_ingredients': recipe_ingredients,
        'recipe_allergens': recipe_allergens,
        'instructions': instructions,
    }
    
    return render(request, 'usereditrecipe.html', context)

# @login_required
# def review_recipe(request, recipe_id):
    
#     if request.method == 'POST':
#         review_text = request.POST.get('review')
#         user_id = request.user.id

#         review = Review(recipe_id=recipe_id, user_id=user_id, review_text=review_text)
#         review.save()

#         messages.success(request, "Your review has been submitted.")
#         return redirect('recipe_detail', recipe_id=recipe_id,reviews=True)
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages

def review_recipe(request, recipe_id):
    if request.method == 'POST':
        # Check if user is logged in using session
        user_id = request.session.get('id')
        if not user_id:
            messages.error(request, 'Please log in to submit a review.')
            return redirect('recipe_detail', recipe_id=recipe_id)

        review_text = request.POST.get('review')
        if review_text:
            # Create new review
            review = Review(
                recipe_id=recipe_id,
                user_id=user_id,
                review_text=review_text
            )
            review.save()
            messages.success(request, 'Your review has been submitted successfully!')
        else:
            messages.error(request, 'Review text cannot be empty.')
            
    return redirect('recipe_detail', recipe_id=recipe_id)


def profile_view(request):
    user_id = request.session.get('id')
    if not user_id:
        messages.error(request, 'Please log in to view your profile.')
        return redirect('login')
    
    try:
        user = CustomUser.objects.get(id=user_id)
        user_recipes = Recipe.objects.filter(user_id=user_id)
        
        # Calculate total time for each recipe
        for recipe in user_recipes:
            recipe.total_time = recipe.prep_time + recipe.cook_time
        
        context = {
            'user': user,
            'user_recipes': user_recipes,
        }
        return render(request, 'profile.html', context)
        
    except CustomUser.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('login')

def profile_edit(request):
    user_id = request.session.get('id')
    if not user_id:
        messages.error(request, 'Please log in to edit your profile.')
        return redirect('login')
    
    try:
        user = CustomUser.objects.get(id=user_id)
        
        if request.method == 'POST':
            field = request.POST.get('field')
            value = request.POST.get(field)
            
            if field in ['address', 'cooking_experience', 'favorite_cuisine', 'allergies']:
                setattr(user, field, value)
                user.save()
                messages.success(request, f'Your {field.replace("_", " ")} has been updated.')
                return redirect('profile')
                
        return render(request, 'edit_profile.html', {'user': user})
        
    except CustomUser.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('login')

def profile_change(request):
    if request.method == 'POST':
        user_id = request.POST.get('id')
        try:
            user = CustomUser.objects.get(id=user_id)
            
            # Update basic info
            user.name = request.POST.get('name')
            user.email = request.POST.get('email')
            user.age = request.POST.get('age')
            user.mobile = request.POST.get('mobile')
            user.date_of_birth = request.POST.get('date_of_birth') or None
            user.address = request.POST.get('address')
            
            # Update preferences
            user.diet_preference = request.POST.get('diet_preference')
            user.cooking_experience = request.POST.get('cooking_experience')
            user.favorite_cuisine = request.POST.get('favorite_cuisine')
            user.allergies = request.POST.get('allergies')
            user.bio = request.POST.get('bio')

            # Handle profile image
            if request.FILES.get('profile_image'):
                user.profile_image = request.FILES['profile_image']

            user.save()
            request.session['username'] = user.name
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
            
        except CustomUser.DoesNotExist:
            messages.error(request, 'User not found.')
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
    
    return redirect('profile')

# 
# 
#

  
# ADMIN DASHBOARD VIEW
#@login_required(login_url='login')
def admin_dashboard(request):
    if not request.session.get('id'):
        return redirect('login')
        
    try:
        user = CustomUser.objects.get(id=request.session.get('id'))
        if not user.is_admin:
            return redirect('homepage')
            
        events = Event.objects.all().order_by('-created_at')
        event_data = []
        
        for event in events:
            try:
                organizer = CustomUser.objects.get(id=event.user_id)
                event.organizer = organizer
            except CustomUser.DoesNotExist:
                event.organizer = None
            event_data.append(event)
            
        context = {
            'total_events': Event.objects.count(),
            'active_events': Event.objects.filter(status='upcoming').count(),
            'total_registrations': EventRegistration.objects.count(),
            'total_organizers': Event.objects.values('user_id').distinct().count(),
            'events': event_data,
            'recipes': Recipe.objects.all(),
            'users': CustomUser.objects.all()
        }
        
        return render(request, 'admin_dashboard.html', context)
        
    except CustomUser.DoesNotExist:
        return redirect('login')
    
def block_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_blocked = True
    user.save()
    return redirect('admin_dashboard')

def add_user(request):
    # Implement user creation logic
    pass

def edit_user(request, user_id):
    # Implement user editing logic
    pass
  # Adjust the redirect as necessary

def unblock_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_blocked = False
    user.save()
    return redirect('admin_dashboard') # Adjust the redirect as necessary

def manage_users(request):
    return render(request, 'manage_users.html')

def manage_subcategories(request):
    return render(request, 'manage_subcategories.html')

def manage_events(request):
    # Get all events
    events = Event.objects.all().order_by('-created_at')
    
    # Get all users in a single query to avoid multiple database hits
    user_dict = {user.id: user for user in CustomUser.objects.all()}
    
    # Attach user objects to events
    for event in events:
        event.user = user_dict.get(event.user_id)
    
    context = {
        'events': events,
        'creator_count': Event.objects.values('user_id').distinct().count(),
        'active_events_count': Event.objects.filter(status='upcoming').count()
    }
    return render(request, 'manage_events.html', context)





#############################################################
#RECIPE MANAGER DASHBOARD VIEW
def admin_dashboard(request):
    recipes = Recipe.objects.all() # List all recipes
    users = CustomUser.objects.all() # List all users
    #pending_recipes = Recipe.objects.filter(status='pending')  # List pending recipes
    context = {'recipes': recipes, 'users': users}##########
    return render(request, 'admin_dashboard.html',context)

##recipe manager add_recipe
#code for add_recipe in recipe manager dashboard
def add_recipe(request):
    if 'id' not in request.session:
        return redirect('login')

    if request.method == 'POST':
        recipe_form = RecipeForm(request.POST, request.FILES)
        nutritional_info_form = NutritionalInformationForm(request.POST)

        if recipe_form.is_valid() and nutritional_info_form.is_valid():
            recipe = recipe_form.save(commit=False)
            
            # If an image was uploaded, classify it
            if 'image' in request.FILES:
                try:
                    classifier = RecipeImageClassifier()
                    classification = classifier.classify_image(request.FILES['image'])
                    
                    # Add classification results to recipe
                    recipe.image_category = classification['category']
                    recipe.category_confidence = classification['confidence']
                    
                    # If it's not a food image, add a message
                    if not classification['is_food']:
                        messages.warning(request, "The uploaded image might not be a food image.")
                        
                except Exception as e:
                    messages.error(request, f"Error classifying image: {str(e)}")
            
            recipe.save()
            
            # Save nutritional info
            nutritional_info = nutritional_info_form.save(commit=False)
            nutritional_info.recipe = recipe
            nutritional_info.save()

            messages.success(request, 'Recipe added successfully!')
            return redirect('admin_dashboard')
    else:
        recipe_form = RecipeForm()
        nutritional_info_form = NutritionalInformationForm()
    
    category = Category.objects.all()
    return render(request, 'add_recipe.html', {
        'recipe_form': recipe_form,
        'nutritional_info_form': nutritional_info_form,
        'categories': category,
    })
#code for edit_recipe in recipe manager dashboard
def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Update basic recipe information
                recipe.recipename = request.POST.get('recipename')
                recipe.category_id = request.POST.get('category')
                recipe.tags = request.POST.get('tags')
                
                if 'image' in request.FILES:
                    recipe.image = request.FILES['image']
                elif 'clear_image' in request.POST:
                    recipe.image = None

                # Handle ingredients
                RecipeIngredient.objects.filter(recipe=recipe).delete()
                ingredient_ids = request.POST.getlist('ingredient[]')
                quantities = request.POST.getlist('quantity[]')
                measurements = request.POST.getlist('measurement[]')

                for i in range(len(ingredient_ids)):
                    ingredient = get_object_or_404(Ingredient, ingredient_id=ingredient_ids[i])
                    RecipeIngredient.objects.create(
                        recipe=recipe,
                        ingredient=ingredient,
                        quantity=quantities[i],
                        measurement=measurements[i]
                    )

                # Handle instructions
                instructions = request.POST.getlist('instructions[]')
                recipe.instructions = '\n'.join(filter(None, instructions))  # Join non-empty instructions

                recipe.save()

                messages.success(request, "Recipe updated successfully!")
                return redirect('admin_dashboard')
        except Exception as e:
            logger.error(f"Error updating recipe {recipe_id}: {str(e)}")
            messages.error(request, f"An error occurred while updating the recipe: {str(e)}")
    
    context = {
        'recipe': recipe,
        'recipe_ingredients': recipe.recipe_ingredients.all(),
        'all_ingredients': Ingredient.objects.all(),
        'categories': Category.objects.all(),
        'instructions': recipe.instructions.split('\n') if recipe.instructions else [],
    }
    return render(request, 'edit_recipe.html', context)

#code for delete_recipe in recipe manager dashboard
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    recipe.delete()
    return redirect('admin_dashboard')


from django.db.models import F
#View to list all ingredients
def ingredient_list(request):
    query = request.GET.get('q')  # Get the query parameter from the URL
    if query:  # If a query is provided
        ingredients = Ingredient.objects.filter(name__icontains=query)  # Filter ingredients
    else:  # If no query is provided
        ingredients = Ingredient.objects.all().order_by(F('name').asc(nulls_last=True))  # Get all ingredients

    return render(request, 'ingredient_list.html', {'ingredients': ingredients, 'query': query})

# # View to add a new ingredient
@require_http_methods(["GET", "POST"])
def add_ingredient(request):
    if request.method == 'POST':
        try:
            # Get the category ID from the form data
            category_id = request.POST.get('category_id')
            name = request.POST.get('name')
            
            # Create the ingredient
            ingredient = Ingredient.objects.create(
                name=name,
                category_id=category_id
            )
            
            # Return JSON response for AJAX requests
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'id': ingredient.ingredient_id,
                    'name': ingredient.name
                })
            
            messages.success(request, 'Ingredient added successfully!')
            return redirect('ingredient_list')
            
        except Exception as e:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=400)
            messages.error(request, f'Error adding ingredient: {str(e)}')
    
    return render(request, 'add_ingredient.html', {'form': IngredientForm()})

# View to edit an existing ingredient
def edit_ingredient(request, ingredient_id):
    ingredient = get_object_or_404(Ingredient, ingredient_id=ingredient_id)  # Ensure using correct field name
    ingredients = Ingredient.objects.all()  # Fetch all existing ingredients
    categories = Category.objects.all()  # Fetch all categories

    if request.method == 'POST':
        form = IngredientForm(request.POST, instance=ingredient)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/ingredients/')
    else:
        form = IngredientForm(instance=ingredient)

    context = {
        'form': form,
        'ingredient': ingredient,
        'ingredients': ingredients,
        'categories': categories,
    }

    return render(request, 'edit_ingredient.html', context)

def delete_ingredient(request, ingredient_id):
    ingredient = get_object_or_404(Ingredient, ingredient_id=ingredient_id)  # Use ingredient_id instead of id
    if request.method == 'POST':
        ingredient.delete()
        return redirect('ingredient_list')  # Redirect after deletion
    return render(request, 'delete_ingredient.html', {'ingredient': ingredient})

from .decorators import admin_required
# admin nutritional info 
def nutritional_info_list(request):
    nutritional_infos = NutritionalInformation.objects.all()
    recipes = Recipe.objects.all()
    return render(request, 'nutritional_info_list.html', {
        'nutritional_infos': nutritional_infos,
        'recipes': recipes
    })

@admin_required
# View to add new nutritional information
def add_edit_nutritional_info(request, recipe_id):
    if recipe_id == 0:
        # This is a new nutritional info, so we need to get the recipe_name from GET parameters
        recipe_name = request.GET.get('recipe_name')
        if not recipe_name:
            return redirect('nutritional_info_list')
        recipe = get_object_or_404(Recipe, recipename=recipe_name)
    else:
        nutritional_info = get_object_or_404(NutritionalInformation, nutritional_info_id=recipe_id)
        recipe = get_object_or_404(Recipe, recipe_id=nutritional_info.recipe_id)

    if request.method == 'POST':
        form = NutritionalInformationForm(request.POST, instance=nutritional_info if recipe_id != 0 else None)
        if form.is_valid():
            nutritional_info = form.save(commit=False)
            nutritional_info.recipe_id = recipe.recipe_id
            nutritional_info.save()
            return redirect('nutritional_info_list')
    else:
        form = NutritionalInformationForm(instance=nutritional_info if recipe_id != 0 else None)

    return render(request, 'add_edit_nutritional_info.html', {'form': form, 'recipe': recipe})

@admin_required
# View to delete nutritional information
def delete_nutritional_info(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if recipe.nutritional_info_id:
        NutritionalInformation.objects.filter(pk=recipe.nutritional_info_id).delete()
        recipe.nutritional_info_id = None
        recipe.save()
        messages.success(request, 'Nutritional information deleted successfully.')
    return redirect('recipe_detail', recipe_id=recipe_id)

#admincan manage categories
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category_list.html', {'categories': categories})

# View to add a new category
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')  # Redirect to the category list
    else:
        form = CategoryForm()
    return render(request, 'add_category.html', {'form': form})

# View to edit an existing category
def edit_category(request, category_id):
    category = get_object_or_404(Category, category_id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')  # Redirect to the category list after editing
    else:
        form = CategoryForm(instance=category)
    return render(request, 'edit_category.html', {'form': form})

# View to delete a category
def delete_category(request, category_id):
    category = get_object_or_404(Category, category_id=category_id)
    print(category.status)
    category.status=False
    category.save()
    return redirect('category_list')  # Redirect to the category list after deletion

def enable_category(request, category_id):
    category = get_object_or_404(Category, category_id=category_id)
    print(category.status)
    category.status=True
    category.save()
    return redirect('category_list')

def user_contact_recipemanager(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Process the form data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            # Send the email
            send_mail(
                f'Contact Form Submission from {name}',
                message,
                email,
                ['support@example.com'],  # Replace with your support email
            )

            return redirect('user_contact_recipemanager_success')
    else:
        form = ContactForm()

    return render(request, 'user_contact_recipemanager.html', {'form': form})

def user_contact_recipemanager_success(request):
    return render(request, 'user_contact_recipemanager_success.html')


def faq(request):
     
     return render(request, 'faq.html')

def subcategory_list(request):
    subcategories = SubCategory.objects.all()
    categories = {category.category_id: category.name for category in Category.objects.all()}
    
    for subcategory in subcategories:
        subcategory.category_name = categories.get(subcategory.category_id, "Unknown Category")
    
    return render(request, 'subcategory_list.html', {'subcategories': subcategories})

def add_subcategory(request):
     if request.method == 'POST':
         form = SubCategoryForm(request.POST)
         if form.is_valid():
             form.save()
             messages.success(request, 'Subcategory added successfully.')
             return redirect('subcategory_list')
     else:
         form = SubCategoryForm()
     return render(request, 'subcategory_form.html', {'form': form, 'action': 'Add'})

def edit_subcategory(request, subcategory_id):
    subcategory = get_object_or_404(SubCategory, subcategory_id=subcategory_id)
    if request.method == 'POST':
        form = SubCategoryForm(request.POST, instance=subcategory)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subcategory updated successfully.')
            return redirect('subcategory_list')
    else:
        form = SubCategoryForm(instance=subcategory)
    return render(request, 'subcategory_form.html', {'form': form, 'action': 'Edit'})


def delete_subcategory(request, subcategory_id):
    subcategory = get_object_or_404(SubCategory, subcategory_id=subcategory_id)
    if request.method == 'POST':
        subcategory.delete()
        messages.success(request, 'Subcategory deleted successfully.')
        return redirect('subcategory_list')
    return render(request, 'subcategory_confirm_delete.html', {'subcategory': subcategory})

@login_required
def rate_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    user_rating = request.POST.get('rating')

    # Check if the user has already rated this recipe
    rating, created = Rating.objects.get_or_create(user=request.user, recipe=recipe)
    rating.rating = user_rating
    rating.save()

    return redirect('recipe_detail', recipe_id=recipe.id)


@login_required
def comment_on_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    comment_text = request.POST.get('comment')

    # Create a new comment
    comment = Comment.objects.create(user=request.user, review=review, comment_text=comment_text)
    comment.save()

    return redirect('recipe_detail', recipe_id=review.recipe.id)

from django.http import HttpResponseRedirect, JsonResponse
from django.http import JsonResponse

from django.http import JsonResponse
from django.core.serializers import serialize
import json

def get_ingredients(request, category_id):
    if request.method == 'GET':
        # Filter ingredients based on the category_id passed in the URL
        if category_id == 1:
            ingredients = Ingredient.objects.filter(category_id=category_id)
        else:
            ingredients = Ingredient.objects.all()
        ingredient_list = [{'id': ingredient.ingredient_id, 'name': ingredient.name} for ingredient in ingredients]
        return JsonResponse({'ingredients': ingredient_list})


# def get_subcategories(request, category_id):
#     subcategories = SubCategory.objects.filter(category_id=category_id).values('id', 'name')
#     return JsonResponse({'subcategories': list(subcategories)})

def get_subcategories(request, category_id):
    subcategories = SubCategory.objects.filter(category_id=category_id).values('subcategory_id', 'name')
    return JsonResponse({'subcategories': list(subcategories)})

def search_suggestions(request):
    query = request.GET.get('query', '').strip()
    if not query:
        return JsonResponse([], safe=False)

    recipes = Recipe.objects.filter(
        Q(recipename__icontains=query) |
        Q(description__icontains=query) |
        Q(category__icontains=query)
    )[:10]  # Limit to 10 suggestions

    suggestions = [{
        'name': recipe.recipename,
        'category': recipe.category,
        'url': reverse('recipe_detail', args=[recipe.recipe_id])
    } for recipe in recipes]

    return JsonResponse(suggestions, safe=False)

def workshop_view(request):
    workshops = {
        'upcoming_workshops': [
            {
                'title': 'Italian Cuisine Masterclass',
                'date': 'April 15, 2024',
                'time': '2:00 PM - 5:00 PM',
                'chef': 'Chef Mario Rossi',
                'price': 'Rs. 1500',
                'spots': '15 spots left',
                'description': 'Learn authentic Italian cooking techniques...',
                'image': 'images/italian-workshop.jpg',
                'topics': ['Pasta Making', 'Sauce Basics', 'Italian Desserts']
            },
             {
                'title': 'Indian Spice Journey',
                'date': 'April 20, 2024',
                'time': '3:00 PM - 6:00 PM',
                'chef': 'Chef Rahul Sharma',
                'price': 'Rs. 1000',
                'spots': '10 spots left',
                'description': 'Dive into the world of Indian spices and learn how to create authentic Indian dishes. From curry basics to bread making, discover the secrets of balancing spices and creating authentic flavors.',
                'image': 'images/indian-workshop.jpg',
                'topics': ['Spice Blending', 'Curry Mastery', 'Bread Making']
            },
           
            {
                'title': 'French Pastry Excellence',
                'date': 'May 1, 2024',
                'time': '10:00 AM - 2:00 PM',
                'chef': 'Chef Sophie Laurent',
                'price': 'Rs. 1600',
                'spots': '12 spots left',
                'description': 'Master the art of French pastry making. Learn to create perfect croissants, eclairs, and macarons. Discover professional techniques and secrets of French baking.',
                'image': 'images/french-pastry.jpg',
                'topics': ['Croissant Making', 'Eclair Mastery', 'Macaron Techniques']
            },

        ]
    }
    return render(request, 'workshop.html', workshops)

def baking_view(request):
    baking_classes = {
        'upcoming_classes': [
            {
                'title': 'Artisan Bread Making',
                'date': 'April 18, 2024',
                'time': '9:00 AM - 1:00 PM',
                'chef': 'Chef Emma Baker',
                'price': 'Rs.1200',
                'spots': '10 spots left',
                'description': 'Master the art of artisan bread making. Learn to create perfect sourdough, baguettes, and rustic loaves using traditional techniques.',
                'image': 'images/bread-making.jpg',
                'topics': ['Sourdough Basics', 'Kneading Techniques', 'Bread Shaping']
            },
            {
                'title': 'French Pastry Essentials',
                'date': 'April 22, 2024',
                'time': '2:00 PM - 6:00 PM',
                'chef': 'Chef Sophie Laurent',
                'price': 'Rs.1500',
                'spots': '8 spots left',
                'description': 'Discover the secrets of French pastry. Create perfect croissants, pain au chocolat, and Danish pastries.',
                'image': 'images/french-pastry.jpg',
                'topics': ['Lamination', 'Pastry Fillings', 'Perfect Layers']
            },
            {
                'title': 'Cake Decorating Masterclass',
                'date': 'April 25, 2024',
                'time': '10:00 AM - 3:00 PM',
                'chef': 'Chef Lisa Thompson',
                'price': 'Rs.1800',
                'spots': '6 spots left',
                'description': 'Learn professional cake decorating techniques. Master fondant, buttercream, and sugar flowers.',
                'image': 'images/cake-decorating.jpg',
                'topics': ['Fondant Work', 'Piping Skills', 'Sugar Flowers']
            }
        ]
    }
    return render(request, 'baking.html', baking_classes)

def food_photography_view(request):
    photography_classes = {
        'upcoming_classes': [
            {
                'title': 'Food Photography Basics',
                'date': 'April 20, 2024',
                'time': '10:00 AM - 2:00 PM',
                'instructor': 'Sarah Williams',
                'price': 'Rs.1500',
                'spots': '12 spots left',
                'description': 'Learn the fundamentals of food photography, from composition to lighting techniques.',
                'image': 'images/photo-basics.jpg',
                'topics': ['Camera Basics', 'Composition', 'Natural Lighting']
            },
            {
                'title': 'Advanced Food Styling',
                'date': 'April 25, 2024',
                'time': '1:00 PM - 5:00 PM',
                'instructor': 'Michael Chen',
                'price': 'Rs.1600',
                'spots': '8 spots left',
                'description': 'Master the art of food styling and learn professional tricks for stunning food presentations.',
                'image': 'images/food-styling.jpg',
                'topics': ['Prop Styling', 'Food Arrangement', 'Color Theory']
            },
            {
                'title': 'Restaurant Photography',
                'date': 'April 30, 2024',
                'time': '3:00 PM - 7:00 PM',
                'instructor': 'Emily Parker',
                'price': 'Rs.1200',
                'spots': '10 spots left',
                'description': 'Specialized workshop for restaurant menu and ambiance photography.',
                'image': 'images/restaurant.jpeg',
                'topics': ['Menu Photography', 'Ambient Light', 'Restaurant Scenes']
            }
        ]
    }
    return render(request, 'food_photography.html', photography_classes)

def event_registration(request, event_id):
    # Get the event details
    event = get_object_or_404(Event, event_id=event_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        
        # Validation
        errors = []
        
        # Name validation
        if not name or not name.replace(' ', '').isalpha():
            errors.append('Name should contain only letters')
        
        # Email validation
        email_regex = r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            errors.append('Please enter a valid email address')
        
        # Phone validation
        if not phone.isdigit() or len(phone) != 10:
            errors.append('Phone number should be 10 digits')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'event_registration.html', {
                'event': event,
                'values': request.POST
            })
        
        try:
            # Check for duplicate registration
            if EventRegistration.objects.filter(email=email, event_id=event_id).exists():
                messages.error(request, 'You have already registered for this event!')
                return render(request, 'event_registration.html', {
                    'event': event,
                    'values': request.POST
                })

            # Save registration
            EventRegistration.objects.create(
                name=name,
                email=email,
                phone=phone,
                event_id=event_id
            )
            
            messages.success(request, 'Registration successful!')
            return redirect('view_events')
            
        except Exception as e:
            messages.error(request, 'Registration failed. Please try again.')
            return render(request, 'event_registration.html', {
                'event': event,
                'values': request.POST
            })
    
    return render(request, 'event_registration.html', {'event': event})

def toggle_favorite(request):
    if request.method == 'POST':
        recipe_id = request.POST.get('recipe_id')
        user_id = request.session.get('id')
        
        if not user_id:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
        
        try:
            recipe = Recipe.objects.get(recipe_id=recipe_id)
            user = CustomUser.objects.get(id=user_id)
            
            favorite, created = Favorite.objects.get_or_create(
                user=user,
                recipe=recipe
            )
            
            if not created:
                favorite.delete()
                is_favorite = False
            else:
                is_favorite = True
                
            return JsonResponse({
                'status': 'success',
                'is_favorite': is_favorite
            })
            
        except (Recipe.DoesNotExist, CustomUser.DoesNotExist):
            return JsonResponse({'error': 'Invalid recipe or user'}, status=400)
            
    return JsonResponse({'error': 'Invalid request'}, status=400)

def create_event(request):
    if not request.session.get('id'):
        messages.error(request, 'Please login to create an event')
        return redirect('login')

    if request.method == 'POST':
        try:
            Event.objects.create(
                user_id=request.session.get('id'),
                title=request.POST.get('title'),
                description=request.POST.get('description'),
                event_type=request.POST.get('event_type'),
                event_date=request.POST.get('event_date'),
                event_time=request.POST.get('event_time'),
                location=request.POST.get('location'),
                max_participants=int(request.POST.get('max_participants')),
                price=request.POST.get('price', 0),
                duration_hours=int(request.POST.get('duration_hours', 1)),
                duration_minutes=int(request.POST.get('duration_minutes', 0)),
                instructor_name=request.POST.get('instructor_name'),
                contact_email=request.POST.get('contact_email'),
                contact_phone=request.POST.get('contact_phone'),
                image=request.FILES.get('image')
            )
            messages.success(request, 'Event created successfully!')
            return redirect('view_events')
        except Exception as e:
            messages.error(request, f'Error creating event: {str(e)}')
    
    return render(request, 'create_event.html')

def my_events(request):
    if not request.session.get('id'):
        messages.error(request, 'Please login to view your events')
        return redirect('login')
    
    events = Event.objects.filter(user_id=request.session.get('id')).order_by('event_date', 'event_time')
    return render(request, 'my_events.html', {'events': events})

def view_events(request):
    if not request.session.get('id'):
        messages.error(request, 'Please login to view events')
        return redirect('login')
    
    # Get all events
    all_events = Event.objects.filter(
        event_date__gte=timezone.now().date()
    ).order_by('event_date', 'event_time')
    
    # Get events created by the current user
    user_events = Event.objects.filter(
        user_id=request.session.get('id')
    ).order_by('event_date', 'event_time')
    
    context = {
        'all_events': all_events,
        'user_events': user_events
    }
    
    return render(request, 'view_events.html', context)

@login_required
def update_profile(request):
    if request.method == 'POST':
        field = request.POST.get('field')
        value = request.POST.get(field)
        user = CustomUser.objects.get(id=request.session.get('id'))
        
        if field in ['address', 'cooking_experience', 'favorite_cuisine', 'allergies']:
            setattr(user, field, value)
            user.save()
            messages.success(request, f'Your {field.replace("_", " ")} has been updated.')
        
        return redirect('profile')
    
    return redirect('profile')

def edit_event(request, event_id):
    if not request.session.get('id'):
        messages.error(request, 'Please login to edit events')
        return redirect('login')
        
    try:
        event = Event.objects.get(event_id=event_id, user_id=request.session.get('id'))
        
        # Add event types for the dropdown
        event_types = [
            ('workshop', 'Workshop'),
            ('class', 'Cooking Class'),
            ('competition', 'Competition'),
            ('tasting', 'Food Tasting'),
            ('seminar', 'Culinary Seminar'),
            ('other', 'Other')
        ]
        
        if request.method == 'POST':
            try:
                event.title = request.POST.get('title')
                event.description = request.POST.get('description')
                event.event_type = request.POST.get('event_type')
                event.event_date = request.POST.get('event_date')
                event.event_time = request.POST.get('event_time')
                event.location = request.POST.get('location')
                event.max_participants = int(request.POST.get('max_participants'))
                event.price = request.POST.get('price', 0)
                event.duration_hours = int(request.POST.get('duration_hours', 1))
                event.duration_minutes = int(request.POST.get('duration_minutes', 0))
                event.contact_email = request.POST.get('contact_email')
                event.contact_phone = request.POST.get('contact_phone')
                
                if 'image' in request.FILES:
                    event.image = request.FILES['image']
                    
                event.save()
                messages.success(request, 'Event updated successfully!')
                return redirect('view_events')
            except Exception as e:
                messages.error(request, f'Error updating event: {str(e)}')
        
        context = {
            'event': event,
            'event_types': event_types
        }
        return render(request, 'edit_event.html', context)
        
    except Event.DoesNotExist:
        messages.error(request, 'Event not found or you do not have permission to edit it')
        return redirect('view_events')

def delete_event(request, event_id):
    if not request.session.get('id'):
        messages.error(request, 'Please login to delete events')
        return redirect('login')
        
    try:
        event = Event.objects.get(event_id=event_id, user_id=request.session.get('id'))
        event.delete()
        messages.success(request, 'Event deleted successfully!')
    except Event.DoesNotExist:
        messages.error(request, 'Event not found or you do not have permission to delete it')
    except Exception as e:
        messages.error(request, f'Error deleting event: {str(e)}')
        
    return redirect('view_events')

def meal_planner(request):
    user_id = request.session.get('id')
    if not user_id:
        return redirect('login')
    
    # Get date range for weekly view
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    # Get meal plans for the week with proper ordering
    weekly_meals = MealPlan.objects.filter(
        user_id=user_id,
        plan_date__range=[week_start, week_end]
    ).order_by('plan_date', 'meal_type')
    
    # Get today's meals
    daily_meals = MealPlan.objects.filter(
        user_id=user_id,
        plan_date=today
    ).order_by('meal_type')
    
    # Get dietary tracking for the week
    weekly_tracking = DietaryTracking.objects.filter(
        user_id=user_id,
        tracking_date__range=[week_start, week_end]
    ).order_by('tracking_date')
    
    # Define meal types and their display order
    meal_types = [
        ('breakfast', 'Breakfast'),
        ('morning_snack', 'Morning Snack'),
        ('lunch', 'Lunch'),
        ('afternoon_snack', 'Afternoon Snack'),
        ('dinner', 'Dinner'),
        ('evening_snack', 'Evening Snack')
    ]
    
    # Create a structured weekly plan
    weekly_plan = []
    current_date = week_start
    while current_date <= week_end:
        day_meals = []
        day_total = {
            'calories': 0,
            'protein': 0,
            'carbs': 0,
            'fat': 0
        }
        
        for meal_type, _ in meal_types:
            meals = [meal for meal in weekly_meals if meal.plan_date == current_date and meal.meal_type == meal_type]
            if meals:
                for meal in meals:
                    # Add meal totals to day totals
                    if 'total_nutrition' in meal.recipe_details:
                        day_total['calories'] += meal.recipe_details['total_nutrition']['calories']
                        day_total['protein'] += meal.recipe_details['total_nutrition']['protein']
                        day_total['carbs'] += meal.recipe_details['total_nutrition']['carbs']
                        day_total['fat'] += meal.recipe_details['total_nutrition']['fat']
            
            day_meals.append({
                'type': meal_type,
                'type_display': dict(meal_types)[meal_type],
                'meals': meals
            })
        
        weekly_plan.append({
            'date': current_date,
            'meals': day_meals,
            'totals': day_total
        })
        current_date += timedelta(days=1)
    
    # Get available recipes for the recipe list
    available_recipes = Recipe.objects.select_related('nutritional_info').all()
    
    context = {
        'weekly_plan': weekly_plan,
        'daily_meals': daily_meals,
        'weekly_tracking': weekly_tracking,
        'week_start': week_start,
        'week_end': week_end,
        'today': today,
        'meal_types': meal_types,
        'available_recipes': available_recipes
    }
    
    return render(request, 'meal_planner.html', context)

@require_http_methods(["GET", "POST"])
def add_meal_plan(request):
    if not request.session.get('id'):
        return JsonResponse({'success': False, 'message': 'Please login to continue'}, status=401)
        
    if request.method == 'POST':
        try:
            # Parse JSON data from request body
            data = json.loads(request.body.decode('utf-8'))
            print("Received data:", data)  # Debug log
            
            # Validate required fields
            if not all(key in data for key in ['plan_date', 'meal_type', 'recipes']):
                return JsonResponse({
                    'success': False,
                    'message': 'Missing required fields'
                }, status=400)
            
            # Validate recipes data
            recipes_data = data.get('recipes', [])
            if not recipes_data:
                return JsonResponse({
                    'success': False,
                    'message': 'At least one recipe is required'
                }, status=400)
            
            print("Processing recipes:", recipes_data)  # Debug log
            
            # Create recipe details list
            recipe_details = []
            total_nutrition = {
                'calories': 0,
                'protein': 0,
                'carbs': 0,
                'fat': 0
            }
            
            for recipe_info in recipes_data:
                recipe_id = recipe_info['recipe_id']
                try:
                    recipe = Recipe.objects.get(recipe_id=recipe_id)
                    recipe_detail = {
                        'recipe_id': recipe_id,
                        'recipe_name': recipe.recipename,
                        'servings': recipe_info['servings'],
                        'calories': recipe_info['calories'],
                        'protein': recipe_info['protein'],
                        'carbs': recipe_info['carbs'],
                        'fat': recipe_info['fat']
                    }
                    recipe_details.append(recipe_detail)
                    
                    # Accumulate nutritional totals
                    total_nutrition['calories'] += float(recipe_info['calories'])
                    total_nutrition['protein'] += float(recipe_info['protein'])
                    total_nutrition['carbs'] += float(recipe_info['carbs'])
                    total_nutrition['fat'] += float(recipe_info['fat'])
                except Recipe.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': f'Recipe with ID {recipe_id} not found'
                    }, status=404)
            
            # Create meal plan
            meal_plan = MealPlan(
                user_id=request.session.get('id'),
                plan_date=data['plan_date'],
                meal_type=data['meal_type'],
                recipe_details={
                    'recipes': recipe_details,
                    'total_nutrition': total_nutrition
                },
                notes=data.get('notes', '')
            )
            meal_plan.save()
            
            # Update dietary tracking
            tracking_date = data['plan_date']
            tracking, created = DietaryTracking.objects.get_or_create(
                user_id=request.session.get('id'),
                tracking_date=tracking_date,
                defaults={
                    'total_calories': 0,
                    'total_protein': 0,
                    'total_carbs': 0,
                    'total_fat': 0
                }
            )
            
            # Update totals
            tracking.total_calories += total_nutrition['calories']
            tracking.total_protein += total_nutrition['protein']
            tracking.total_carbs += total_nutrition['carbs']
            tracking.total_fat += total_nutrition['fat']
            tracking.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Meal plan added successfully'
            })
            
        except json.JSONDecodeError as e:
            print("JSON Decode Error:", str(e))  # Debug log
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            print("Error in add_meal_plan:", str(e))  # Debug log
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
    
    # GET request - render the form
    recipes = Recipe.objects.select_related('nutritional_info').all()
    return render(request, 'add_meal.html', {'recipes': recipes})

def edit_meal(request, meal_id):
    if not request.session.get('id'):
        return redirect('login')
    
    meal = get_object_or_404(MealPlan, id=meal_id, user_id=request.session.get('id'))
    recipes = Recipe.objects.select_related('nutritional_info').all()
    
    if request.method == 'POST':
        try:
            # Get the old values for dietary tracking adjustment
            old_calories = float(meal.recipe_details.get('calories', 0))
            old_protein = float(meal.recipe_details.get('protein', 0))
            old_carbs = float(meal.recipe_details.get('carbs', 0))
            old_fat = float(meal.recipe_details.get('fat', 0))
            
            # Update meal plan
            recipe_id = request.POST.get('recipe_id')
            recipe = Recipe.objects.get(recipe_id=recipe_id)
            
            meal.plan_date = request.POST.get('plan_date')
            meal.meal_type = request.POST.get('meal_type')
            meal.recipe_details = {
                'recipe_id': recipe_id,
                'recipe_name': recipe.recipename,
                'servings': request.POST.get('servings'),
                'calories': request.POST.get('calories'),
                'protein': request.POST.get('protein'),
                'carbs': request.POST.get('carbs'),
                'fat': request.POST.get('fat')
            }
            meal.notes = request.POST.get('notes')
            meal.save()
            
            # Update dietary tracking
            tracking = DietaryTracking.objects.get(
                user_id=request.session.get('id'),
                tracking_date=request.POST.get('plan_date')
            )
            
            # Adjust nutritional totals
            tracking.total_calories = tracking.total_calories - old_calories + float(request.POST.get('calories', 0))
            tracking.total_protein = tracking.total_protein - old_protein + float(request.POST.get('protein', 0))
            tracking.total_carbs = tracking.total_carbs - old_carbs + float(request.POST.get('carbs', 0))
            tracking.total_fat = tracking.total_fat - old_fat + float(request.POST.get('fat', 0))
            tracking.save()
            
            messages.success(request, 'Meal updated successfully!')
            return redirect('meal_planner')
            
        except Exception as e:
            messages.error(request, f'Error updating meal: {str(e)}')
    
    context = {
        'meal': meal,
        'recipes': recipes
    }
    return render(request, 'edit_meal.html', context)

@require_http_methods(["POST"])
def delete_meal_plan(request, meal_id):
    try:
        meal = get_object_or_404(MealPlan, id=meal_id)
        meal.delete()
        return JsonResponse({
            'success': True,
            'message': 'Meal deleted successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

def analyze_recipe_diet(request, recipe_id):
    try:
        recipe = Recipe.objects.get(pk=recipe_id)
        nutritional_info = NutritionalInformation.objects.filter(recipe=recipe).first()
        
        if not nutritional_info:
            return JsonResponse({
                'error': 'Nutritional information not available for this recipe'
            }, status=404)

        condition = request.GET.get('condition', 'diabetic')
        
        # Safely convert servings to float
        try:
            servings = float(recipe.servings) if recipe.servings else 1.0
        except (ValueError, TypeError):
            servings = 1.0

        # Safely convert nutritional values to float
        try:
            calories_per_serving = float(nutritional_info.calories or 0) / servings
            protein_per_serving = float(nutritional_info.protein or 0) / servings
            carbs_per_serving = float(nutritional_info.carbohydrates or 0) / servings
            fat_per_serving = float(nutritional_info.fat or 0) / servings
            fiber_per_serving = float(nutritional_info.fiber or 0) / servings
            sugar_per_serving = float(nutritional_info.sugar or 0) / servings
        except (ValueError, TypeError) as e:
            return JsonResponse({
                'error': 'Invalid nutritional values in database'
            }, status=400)

        # Round values to 1 decimal place for display
        calories_per_serving = round(calories_per_serving, 1)
        protein_per_serving = round(protein_per_serving, 1)
        carbs_per_serving = round(carbs_per_serving, 1)
        fat_per_serving = round(fat_per_serving, 1)
        fiber_per_serving = round(fiber_per_serving, 1)
        sugar_per_serving = round(sugar_per_serving, 1)

        if condition == 'diabetic':
            risk_points = 0
            nutrients = []
            concerns = []
            benefits = []

            # Analyze carbohydrates
            if carbs_per_serving > 45:
                risk_points += 2
                concerns.append(f'High carbohydrate content ({carbs_per_serving}g per serving)')
            elif carbs_per_serving > 30:
                risk_points += 1
            else:
                benefits.append('Moderate carbohydrate content')

            nutrients.append({
                'name': 'Carbohydrates',
                'value': carbs_per_serving,
                'unit': 'g',
                'status': 'high' if carbs_per_serving > 45 else 'normal',
                'min': 15,
                'max': 45,
                'message': 'Keep portions controlled'
            })

            # Analyze sugar
            if sugar_per_serving > 10:
                risk_points += 2
                concerns.append(f'High sugar content ({sugar_per_serving}g per serving)')
            elif sugar_per_serving > 5:
                risk_points += 1
            else:
                benefits.append('Low sugar content')

            nutrients.append({
                'name': 'Sugar',
                'value': sugar_per_serving,
                'unit': 'g',
                'status': 'high' if sugar_per_serving > 10 else 'normal',
                'min': 0,
                'max': 10,
                'message': 'Monitor blood sugar after eating'
            })

            # Analyze fiber
            if fiber_per_serving < 3:
                risk_points += 1
                concerns.append('Low fiber content')
            else:
                benefits.append('Good fiber content')

            nutrients.append({
                'name': 'Fiber',
                'value': fiber_per_serving,
                'unit': 'g',
                'status': 'low' if fiber_per_serving < 3 else 'normal',
                'min': 3,
                'max': None,
                'message': 'Helps regulate blood sugar'
            })

            # Calculate risk level
            if risk_points >= 3:
                risk_level = 'High'
                can_eat = False
            elif risk_points >= 2:
                risk_level = 'Moderate'
                can_eat = True
            else:
                risk_level = 'Low'
                can_eat = True

            return JsonResponse({
                'can_eat': can_eat,
                'risk_level': risk_level,
                'nutrients': nutrients,
                'concerns': concerns,
                'benefits': benefits,
                'overall_recommendation': f"This recipe is {'not ' if not can_eat else ''}suitable for diabetics.",
                'serving_recommendation': f"Stick to {recipe.servings} serving(s) or less.",
                'meal_timing_advice': "Best consumed as part of a balanced meal with protein and healthy fats."
            })

        elif condition == 'cholesterol':
            risk_points = 0
            nutrients = []
            concerns = []
            benefits = []

            # Analyze fat
            if fat_per_serving > 20:
                risk_points += 2
                concerns.append(f'High fat content ({fat_per_serving}g per serving)')
            elif fat_per_serving > 15:
                risk_points += 1
            else:
                benefits.append('Moderate fat content')

            nutrients.append({
                'name': 'Total Fat',
                'value': fat_per_serving,
                'unit': 'g',
                'status': 'high' if fat_per_serving > 20 else 'normal',
                'min': 0,
                'max': 20,
                'message': 'Keep fat intake moderate'
            })

            # Analyze fiber
            if fiber_per_serving < 5:
                risk_points += 1
                concerns.append('Low fiber content')
            else:
                benefits.append('Good fiber content for cholesterol management')

            nutrients.append({
                'name': 'Fiber',
                'value': fiber_per_serving,
                'unit': 'g',
                'status': 'low' if fiber_per_serving < 5 else 'normal',
                'min': 5,
                'max': None,
                'message': 'Helps lower cholesterol'
            })

            # Calculate risk level
            if risk_points >= 2:
                risk_level = 'High'
                can_eat = False
            elif risk_points == 1:
                risk_level = 'Moderate'
                can_eat = True
            else:
                risk_level = 'Low'
                can_eat = True

            return JsonResponse({
                'can_eat': can_eat,
                'risk_level': risk_level,
                'nutrients': nutrients,
                'concerns': concerns,
                'benefits': benefits,
                'overall_recommendation': f"This recipe is {'not ' if not can_eat else ''}suitable for those managing cholesterol.",
                'serving_recommendation': f"Stick to {recipe.servings} serving(s) or less.",
                'meal_timing_advice': "Best consumed as part of a balanced meal rich in fiber."
            })

        elif condition == 'blood_pressure':
            risk_points = 0
            nutrients = []
            concerns = []
            benefits = []

            # Analyze fat content
            if fat_per_serving > 15:
                risk_points += 2
                concerns.append(f'High fat content ({fat_per_serving}g per serving)')
            elif fat_per_serving > 10:
                risk_points += 1
            else:
                benefits.append('Moderate fat content')

            nutrients.append({
                'name': 'Total Fat',
                'value': fat_per_serving,
                'unit': 'g',
                'status': 'high' if fat_per_serving > 15 else 'normal',
                'min': 0,
                'max': 15,
                'message': 'Keep fat intake moderate'
            })

            # Analyze calories
            if calories_per_serving > 500:
                risk_points += 1
                concerns.append('High calorie content')
            else:
                benefits.append('Moderate calorie content')

            nutrients.append({
                'name': 'Calories',
                'value': calories_per_serving,
                'unit': 'kcal',
                'status': 'high' if calories_per_serving > 500 else 'normal',
                'min': 0,
                'max': 500,
                'message': 'Monitor portion sizes'
            })

            # Calculate risk level
            if risk_points >= 2:
                risk_level = 'High'
                can_eat = False
            elif risk_points == 1:
                risk_level = 'Moderate'
                can_eat = True
            else:
                risk_level = 'Low'
                can_eat = True

            return JsonResponse({
                'can_eat': can_eat,
                'risk_level': risk_level,
                'nutrients': nutrients,
                'concerns': concerns,
                'benefits': benefits,
                'overall_recommendation': f"This recipe is {'not ' if not can_eat else ''}suitable for those with blood pressure concerns.",
                'serving_recommendation': f"Stick to {recipe.servings} serving(s) or less.",
                'meal_timing_advice': "Best consumed as part of a balanced meal with plenty of vegetables."
            })

        elif condition == 'kidney_disease':
            risk_points = 0
            nutrients = []
            concerns = []
            benefits = []

            # Analyze protein
            if protein_per_serving > 15:
                risk_points += 2
                concerns.append(f'High protein content ({protein_per_serving}g per serving)')
            elif protein_per_serving > 10:
                risk_points += 1
            else:
                benefits.append('Moderate protein content')

            nutrients.append({
                'name': 'Protein',
                'value': protein_per_serving,
                'unit': 'g',
                'status': 'high' if protein_per_serving > 15 else 'normal',
                'min': 0,
                'max': 15,
                'message': 'Keep protein intake moderate'
            })

            # Calculate risk level
            if risk_points >= 2:
                risk_level = 'High'
                can_eat = False
            elif risk_points == 1:
                risk_level = 'Moderate'
                can_eat = True
            else:
                risk_level = 'Low'
                can_eat = True

            return JsonResponse({
                'can_eat': can_eat,
                'risk_level': risk_level,
                'nutrients': nutrients,
                'concerns': concerns,
                'benefits': benefits,
                'overall_recommendation': f"This recipe is {'not ' if not can_eat else ''}suitable for those with kidney disease.",
                'serving_recommendation': f"Stick to {recipe.servings} serving(s) or less.",
                'meal_timing_advice': "Space protein intake throughout the day."
            })

    except Recipe.DoesNotExist:
        return JsonResponse({'error': 'Recipe not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def analyze_nutrient_for_condition(name, value, range_info):
    """Analyze a nutrient value against condition-specific ranges."""
    min_val = range_info['min']
    max_val = range_info['max']
    unit = range_info['unit']
    
    if max_val and value > max_val:
        status = 'high'
        message = f"{name} content is too high - consider reducing portion size"
    elif value < min_val:
        status = 'low'
        message = f"{name} content is below recommended minimum"
    else:
        status = 'normal'
        message = f"{name} content is within acceptable range"
    
    return {
        'name': name,
        'value': value,
        'min': min_val,
        'max': max_val,
        'unit': unit,
        'status': status,
        'message': message
    }
