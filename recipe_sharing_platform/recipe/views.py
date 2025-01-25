import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from .models import CustomUser, SubCategory, Recipe, NutritionalInformation, Ingredient, Category, Rating, Review, Comment, RecipeIngredient, EventRegistration
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


logger = logging.getLogger(__name__)

#USER DASHBOARD
def signup(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        #mobile = request.POST.get('mobile')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return redirect('signup')

        user = CustomUser(name=name, email=email, password=password1)
        user.save()
        if user:
            messages.success(request, 'Account created successfully')
            return redirect('login')  # Redirect to homepage after signup
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
       context = {}
       if request.user:
           if request.user.is_admin:
               context['admin_message'] = "Welcome, Admin!"
           else:
               context['user_message'] = f"Welcome, {request.user.name}!"
       else:
           context['guest_message'] = "Welcome, Guest! Please log in or sign up."
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
            # Extract basic recipe information
            recipename = request.POST.get('recipename')
            category_id = request.POST.get('category')
            subcategory_id = request.POST.get('subcategory')
            tags = request.POST.get('tags')
            image = request.FILES.get('image')
            servings = request.POST.get('servings')
            prep_time = request.POST.get('prep_time')
            cook_time = request.POST.get('cook_time')

            # Collect all instructions
            instructions = []
            for key, value in request.POST.items():
                if key.startswith('instructions_') and value.strip():
                    instructions.append(value.strip())
            instructions = '\n'.join(instructions)

            # Validate fields
            if not all([recipename, category_id, tags, instructions, servings, prep_time, cook_time]):
                raise ValueError('All fields except image are required!')

            # Create Recipe
            recipe = Recipe.objects.create(
                recipename=recipename,
                category_id=category_id,
                subcategory_id=subcategory_id,
                tags=tags,
                instructions=instructions,
                image=image,
                user_id=request.session.get('id'),  # Assuming user ID is stored in session
                servings=servings,
                prep_time=prep_time,
                cook_time=cook_time
            )

            # Process ingredients
            ingredient_count = 1
            while True:
                ingredient_id = request.POST.get(f'ingredient_{ingredient_count}')
                ingredient_name = request.POST.get(f'ingredient_name_{ingredient_count}')
                quantity = request.POST.get(f'quantity_{ingredient_count}')
                measurement = request.POST.get(f'measurement_{ingredient_count}')

                if not all([ingredient_id, quantity, measurement]):
                    break

                if ingredient_id.startswith('new_'):
                    # Create a new ingredient
                    new_ingredient = Ingredient.objects.create(name=ingredient_name)
                    ingredient_id = new_ingredient.ingredient_id

                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient_id=ingredient_id,
                    quantity=quantity,
                    measurement=measurement
                )

                ingredient_count += 1

            messages.success(request, 'Recipe added successfully!')
            return redirect('recipe')

        except ValueError as ve:
            messages.error(request, str(ve))  # Catch specific validation error
        except Exception as e:
            messages.error(request, f'Error adding recipe: {str(e)}')  # General error

    # Fetch categories and ingredients for the form
    categories = Category.objects.filter(status=True)
    ingredients = Ingredient.objects.all()
    return render(request, 'addrecipe.html', {'categories': categories, 'ingredients': ingredients})

def recipe_detail(request, recipe_id, reviews=False):
    recipe = get_object_or_404(Recipe, recipe_id=recipe_id)
    
    # Get the user_id from request.session
    user_id = request.session.get('id')
    is_logged_in = user_id is not None
    
    try:
        # Modified this part to include user information
        reviews = Review.objects.filter(recipe_id=recipe_id).values(
            'review_id', 
            'user_id', 
            'review_text', 
            'created_at'
        ).order_by('-created_at')
        
        # Fetch user names for all reviews
        for review in reviews:
            try:
                user = CustomUser.objects.get(id=review['user_id'])
                review['user_name'] = user.name
            except CustomUser.DoesNotExist:
                review['user_name'] = "Unknown User"
    except:
        reviews = []

    # Get ratings
    ratings = Rating.objects.filter(recipe_id=recipe_id)
    average_rating = ratings.aggregate(Avg('rating'))['rating__avg']
    total_ratings = ratings.count()
    
    # Get user's rating if they've rated
    user_rating = None
    if request.session.get('id'):
        user_rating = Rating.objects.filter(
            recipe_id=recipe_id,
            user_id=request.session['id']
        ).first()

    # Fetch the category name
    category = Category.objects.filter(category_id=recipe.category_id).first()
    category_name = category.name if category else "Unknown Category"
    
    # Split instructions into a list
    instructions = [inst.strip() for inst in recipe.instructions.split('\n') if inst.strip()]
    
    # Fetch nutritional information
    try:
        nutritional_info = NutritionalInformation.objects.get(recipe_id=recipe_id)
    except NutritionalInformation.DoesNotExist:
        nutritional_info = None
     
    # Fetch ingredients
    ingredients = recipe.recipe_ingredients.all().select_related('ingredient')
    
    # Fetch subcategory name
    subcategory = SubCategory.objects.filter(subcategory_id=recipe.subcategory_id).first()
    subcategory_name = subcategory.name if subcategory else "Unknown Subcategory"
    
    # Check if the user is an admin
    is_admin = request.user.is_admin if hasattr(request.user, 'is_admin') else False
    
    context = {
        'recipe': recipe,
        'category_name': category_name,
        'instructions': instructions,
        'messages': messages.get_messages(request),
        'reviews': reviews,
        'reviews_display': True,
        'nutritional_info': nutritional_info,
        'is_admin': is_admin,
        'ingredients': ingredients,
        'subcategory_name': subcategory_name,
        'average_rating': average_rating,
        'total_ratings': total_ratings,
        'user_rating': user_rating,
        'is_logged_in': is_logged_in,  # Add this to context
        'user_id': user_id,  # Add this to context
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
                return redirect('recipe_detail', recipe_id=recipe.recipe_id)
        except Exception as e:
            logger.error(f"Error updating recipe {recipe_id}: {str(e)}")
            messages.error(request, f"An error occurred while updating the recipe: {str(e)}")
    else:
        form = RecipeForm(instance=recipe)

    context = {
        'recipe': recipe,
        'form': form,
        'recipe_ingredients': recipe.recipe_ingredients.all(),
        'all_ingredients': Ingredient.objects.all(),
        'categories': Category.objects.all(),
        'instructions': recipe.instructions.split('\n') if recipe.instructions else [],
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
    # Get user_id from session
    user_id = request.session.get('id')
    if not user_id:
        messages.error(request, 'Please log in to view your profile.')
        return redirect('login')
        
    try:
        user = CustomUser.objects.get(id=user_id)
        # Fetch recipes for this user
        recipes = Recipe.objects.filter(user_id=user_id).order_by('-recipe_id')  # Most recent first
        
        context = {
            'user': user,
            'recipes': recipes
        }
        return render(request, 'profile.html', context)
    except CustomUser.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('login')

def profile_edit(request):
    # Get user_id from session
    user_id = request.session.get('id')
    if not user_id:
        messages.error(request, 'Please log in to edit your profile.')
        return redirect('login')
    
    try:
        user = CustomUser.objects.get(id=user_id)
        return render(request, 'edit_profile.html', {'user': user})
    except CustomUser.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('login')

def profile_change(request):
    if request.method == 'POST':
        username=request.POST.get('name')
        email=request.POST.get('email')
        userid=request.POST.get('id')
        user=CustomUser.objects.get(id=userid)
        if user:
            user.name=username
            user.email=email
            user.save()
            request.session['username'] = username
            customer=CustomUser.objects.get(id=userid)
            return render(request,'profile.html',{'user':customer})

# 
# 
#

  
# ADMIN DASHBOARD VIEW
#@login_required(login_url='login')
def admin_dashboard(request):
    if request.user and request.user.is_admin:
        # User is an admin, fetch data and show admin dashboard
        recipes = Recipe.objects.all()
        users = CustomUser.objects.all()
        context = {
            'recipes': recipes,
            'users': users,
        }
        return render(request, 'admin_dashboard.html', context)
    else:
        # User is not an admin, show error and redirect
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('homepage')
    
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
    return render(request, 'manage_events.html')






















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
    # Check if the user is logged in by verifying 'id' in the session
    if 'id' not in request.session:
        return redirect('login')  # Redirect to login page if not logged in

    if request.method == 'POST':
        recipe_form = RecipeForm(request.POST, request.FILES)
        nutritional_info_form = NutritionalInformationForm(request.POST)

        if recipe_form.is_valid() and nutritional_info_form.is_valid():
            recipe = recipe_form.save()  # Save the recipe first
            nutritional_info = nutritional_info_form.save(commit=False)  # Do not save yet
            nutritional_info.recipe = recipe  # Link it to the recipe
            nutritional_info.save()  # Now save the nutritional info

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
from django.views.decorators.http import require_http_methods
@require_http_methods(["GET", "POST"])
def add_ingredient(request):
    if request.method == 'POST':
        form = IngredientForm(request.POST)
        if form.is_valid():
            ingredient = form.save()
            
            # Check if it's an AJAX request
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'id': ingredient.ingredient_id,
                    'name': ingredient.name
                })
            else:
                messages.success(request, 'Ingredient added successfully!')
                return redirect('ingredient_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
    else:
        form = IngredientForm()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'errors': 'Invalid request'}, status=400)
    
    return render(request, 'add_ingredient.html', {'form': form})

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

def event_registration(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        event = request.POST.get('event')
        
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
        
        # Event validation
        if not event:
            errors.append('Please select an event')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'event_registration.html', {'values': request.POST})
        
        try:
            # Check for duplicate registration
            if EventRegistration.objects.filter(email=email, event=event).exists():
                messages.error(request, 'You have already registered for this event!')
                return render(request, 'event_registration.html', {'values': request.POST})

            # Save registration
            EventRegistration.objects.create(
                name=name,
                email=email,
                phone=phone,
                event=event
            )
            
            messages.success(request, 'Registration successful! We will contact you soon.')
            return redirect('homepage')
            
        except Exception as e:
            messages.error(request, 'Registration failed. Please try again.')
            return render(request, 'event_registration.html', {'values': request.POST})
    
    return render(request, 'event_registration.html')

