from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.contrib import messages
from .models import CustomUser
from django.db import IntegrityError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from .forms import CreateUserForm
from .models import Recipe, NutritionalInformation,Ingredient,Category,Rating,Review,Comment
from .forms import RecipeForm, NutritionalInformationForm,ProfileForm,IngredientForm,CategoryForm,CreateUserForm,ContactForm
import random
from django.db.models import Avg
from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail 
import logging
from django.urls import reverse
from django.db import transaction
from .models import Recipe, Category, Ingredient, RecipeIngredient
from django.conf import settings

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
            if(user.email=="recipemanager@gmail.com" and user.password=="RecipeManager@123"):
                return redirect('recipe_manager_dashboard')
            # Directly compare plain text passwords
            else:
                if user.password == password:
                    request.session['username'] = user.name 
                    request.session['email']=user.email
                    request.session['id']=user.id
                    return render(request,'homepage.html')
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
            # Generate a random 4-digit code
            code = random.randint(1000, 9999)
            user_pins[email] = code

            # Send email with the code
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
    return render(request, 'homepage.html')


def recipe(request):
    recipes = Recipe.objects.all()
    for recipe in recipes:
        logger.info(f"Recipe ID: {recipe.recipe_id}, Recipe ID type: {type(recipe.recipe_id)}, Name: {recipe.recipename}")
    return render(request, 'recipe.html', {'recipes': recipes})

#FOR SEARCH PURPOSE ADDED THIS CODE SAME PAGE TOP AND
def recipe(request):
    search_query = request.GET.get('search', '')  # Get the search query from the request
    if search_query:
        recipes = Recipe.objects.filter(recipename__icontains=search_query)
    else:
        recipes = Recipe.objects.all()

    return render(request, 'recipe.html', {'recipes': recipes})


def about(request):
    return render(request, 'about.html' )
#ABOUT VIEW
def contact(request):
    return render(request, 'contact.html')


def addrecipe(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                logger.info(f"POST data: {request.POST}")
                logger.info(f"FILES data: {request.FILES}")

                recipename = request.POST.get('recipename')
                category_id = request.POST.get('category')
                tags = request.POST.get('tags')
                image = request.FILES.get('image')
                
                # Collect all instructions
                instructions = []
                for key, value in request.POST.items():
                    if key.startswith('instructions_') and value.strip():
                        instructions.append(value.strip())
                instructions = '\n'.join(instructions)

                logger.info(f"Parsed data: recipename={recipename}, category_id={category_id}, tags={tags}, image={image}, instructions={instructions[:50]}...")

                # Validate fields
                if not all([recipename, category_id, tags, instructions]):
                    raise ValueError('All fields except image are required!')

                # Create Recipe
                recipe = Recipe.objects.create(
                    recipename=recipename,
                    category_id=category_id,
                    tags=tags,
                    instructions=instructions,
                    image=image
                )

                logger.info(f"Created recipe with ID: {recipe.recipe_id}")

                # Process ingredients
                ingredient_count = 1
                while True:
                    ingredient_id = request.POST.get(f'ingredient_{ingredient_count}')
                    quantity = request.POST.get(f'quantity_{ingredient_count}')
                    measurement = request.POST.get(f'measurement_{ingredient_count}')

                    if not all([ingredient_id, quantity, measurement]):
                        break

                    RecipeIngredient.objects.create(
                        recipe=recipe,
                        ingredient_id=ingredient_id,
                        quantity=quantity,
                        measurement=measurement
                    )
                    logger.info(f"Added ingredient: {ingredient_id}, quantity: {quantity}, measurement: {measurement}")

                    ingredient_count += 1

                messages.success(request, 'Recipe added successfully!')
                return redirect('recipe')

        except Exception as e:
            logger.error(f"Error adding recipe: {str(e)}", exc_info=True)
            messages.error(request, f'Error adding recipe: {str(e)}')

    categories = Category.objects.all()
    ingredients = Ingredient.objects.all()
    return render(request, 'addrecipe.html', {'categories': categories, 'ingredients': ingredients})


def recipe_detail(request, recipe_id,reviews=False):
    recipe = get_object_or_404(Recipe, recipe_id=recipe_id)
    reviews = Review.objects.filter(recipe_id=recipe_id)  # Fetch reviews for the recipe
    
    # Fetch the category name
    category = Category.objects.filter(category_id=recipe.category_id).first()
    category_name = category.name if category else "Unknown Category"
    
    # Split instructions into a list
    instructions = [inst.strip() for inst in recipe.instructions.split('\n') if inst.strip()]
    
    context = {
        'recipe': recipe,
        'category_name': category_name,
        'instructions': instructions,
        'messages': messages.get_messages(request),
        'reviews': reviews, # Pass reviews to the template
        'reviews_display': reviews if reviews else False 
    }
    
    return render(request, 'recipe_detail.html', context)
    



#for edting recipes on recipe page for user
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Recipe
from .forms import RecipeForm

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Recipe
from .forms import RecipeForm
import logging

logger = logging.getLogger(__name__)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Recipe, RecipeIngredient, Ingredient, Category
from .forms import RecipeForm
import logging

logger = logging.getLogger(__name__)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Recipe, RecipeIngredient, Ingredient, Category
from .forms import RecipeForm
from django.db import transaction
import logging

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

@login_required
def review_recipe(request, recipe_id):
    if request.method == 'POST':
        review_text = request.POST.get('review')
        user_id = request.user.id

        review = Review(recipe_id=recipe_id, user_id=user_id, review_text=review_text)
        review.save()

        messages.success(request, "Your review has been submitted.")
        return redirect('recipe_detail', recipe_id=recipe_id,reviews=True)

def profile_view(request,user_id):
    user=CustomUser.objects.get(id=user_id)
    return render(request, 'profile.html', {'user': user})
    

def profile_edit(request,user_id):
    custom=CustomUser.objects.get(id=user_id)
    return render(request, 'edit_profile.html',{'user':custom})
    #return render(request, 'profile.html')

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
#########################################################   
# ADMIN DASHBOARD VIEW
#@login_required(login_url='login')
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

def block_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_blocked = True
    user.save()
    return redirect('admin_dashboard')  # Adjust the redirect as necessary

def unblock_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_blocked = False
    user.save()
    return redirect('admin_dashboard')  # Adjust the redirect as necessary

#############################################################
#RECIPE MANAGER DASHBOARD VIEW
def recipe_manager_dashboard(request):
    recipes = Recipe.objects.all() # List all recipes
    users = CustomUser.objects.all() # List all users
    #pending_recipes = Recipe.objects.filter(status='pending')  # List pending recipes
    context = {'recipes': recipes, 'users': users}##########
    return render(request, 'recipe_manager_dashboard.html',context)

##recipe manager add_recipe
#code for add_recipe in recipe manager dashboard
def add_recipe(request):
    if request.method == 'POST':
        recipe_form = RecipeForm(request.POST, request.FILES)
        nutritional_info_form = NutritionalInformationForm(request.POST)

        if recipe_form.is_valid() and nutritional_info_form.is_valid():
            recipe = recipe_form.save()  # Save the recipe first
            nutritional_info = nutritional_info_form.save(commit=False)  # Do not save yet
            nutritional_info.recipe = recipe  # Link it to the recipe
            nutritional_info.save()  # Now save the nutritional info
            
            return redirect('recipe_manager_dashboard')
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
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            form.save()
            return redirect('recipe_manager_dashboard')
    else:
        form = RecipeForm(instance=recipe)
    return render(request, 'edit_recipe.html', {'form': form, 'recipe': recipe})

#code for delete_recipe in recipe manager dashboard
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    recipe.delete()
    return redirect('recipe_manager_dashboard')


##recipe manager manage_ingredients
#View to list all ingredients
def ingredient_list(request):
    query = request.GET.get('q')  # Get the query parameter from the URL
    if query:  # If a query is provided
        ingredients = Ingredient.objects.filter(name__icontains=query)  # Filter ingredients
    else:  # If no query is provided
        ingredients = Ingredient.objects.all()  # Get all ingredients

    return render(request, 'ingredient_list.html', {'ingredients': ingredients, 'query': query})

# # View to add a new ingredient
def add_ingredient(request):
    if request.method == 'POST':
        form = IngredientForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new ingredient to the database
            return redirect('add_ingredient')  # Redirect to the same page or another page after saving
    else:
        form = IngredientForm()
    
    return render(request, 'add_ingredient.html', {'form': form})

# View to edit an existing ingredient
def edit_ingredient(request, ingredient_id):
    ingredient = get_object_or_404(Ingredient, ingredient_id=ingredient_id)  # Use ingredient_id here
    
    if request.method == 'POST':
        ingredient.name = request.POST.get('name')
        ingredient.substitutions = request.POST.get('substitutions')
        ingredient.category_id = request.POST.get('category_id')  # Make sure to handle category correctly
        ingredient.save()
        return redirect('ingredient_list')  # Redirect after saving

    return render(request, 'edit_ingredient.html', {'ingredient': ingredient})

def delete_ingredient(request, ingredient_id):
    ingredient = get_object_or_404(Ingredient, ingredient_id=ingredient_id)  # Use ingredient_id instead of id
    if request.method == 'POST':
        ingredient.delete()
        return redirect('ingredient_list')  # Redirect after deletion
    return render(request, 'delete_ingredient.html', {'ingredient': ingredient})

#recipe manager manage_nutritional info 
def nutritional_info_list(request):
    nutritional_infos = NutritionalInformation.objects.all()
    return render(request, 'nutritional_info_list.html', {'nutritional_infos': nutritional_infos})

# View to add new nutritional information
def add_nutritional_info(request):
    if request.method == 'POST':
        form = NutritionalInformationForm(request.POST)
        if form.is_valid():
            nutritional_info = form.save(commit=False)
            # You might want to set the recipe_id if needed
            # nutritional_info.recipe_id = some_recipe_id
            nutritional_info.save()
            return redirect('nutritional_info_list')
    else:
        form = NutritionalInformationForm()
    return render(request, 'add_nutritional_info.html', {'form': form})

# View to edit existing nutritional information
def edit_nutritional_info(request, pk):
    nutritional_info = get_object_or_404(NutritionalInformation, pk=pk)
    if request.method == 'POST':
        form = NutritionalInformationForm(request.POST, instance=nutritional_info)
        if form.is_valid():
            form.save()
            return redirect('nutritional_info_list')
    else:
        form = NutritionalInformationForm(instance=nutritional_info)
    return render(request, 'edit_nutritional_info.html', {'form': form})

# View to delete nutritional information
def delete_nutritional_info(request, pk):
    nutritional_info = get_object_or_404(NutritionalInformation, pk=pk)
    if request.method == 'POST':
        nutritional_info.delete()
        return redirect('nutritional_info_list')
    return render(request, 'delete_nutritional_info.html', {'nutritional_info': nutritional_info})

#recipe manager can manage categories
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
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')  # Redirect to the category list after deletion
    return render(request, 'delete_category.html', {'category': category})
##############
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

from .models import FAQ
def faq(request):
    faqs = FAQ.objects.all()
    return render(request, 'faq.html', {'faqs': faqs})
#############################
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

from django.http import JsonResponse
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
# def get_nutritional_info(request, ingredient_id):
#     try:
#         nutrient_info = NutritionalInformation.objects.get(id=ingredient_id)
#         data = {
#             'protein': nutrient_info.protein,
#             'fiber': nutrient_info.fiber,
#             'fat': nutrient_info.fat,
#             'carbohydrates': nutrient_info.carbohydrates,
#             'calories': nutrient_info.calories,
#             'sugars': nutrient_info.sugars,
#         }
#         return JsonResponse(data)
#     except NutritionalInformation.DoesNotExist:
#         return JsonResponse({}, status=404)