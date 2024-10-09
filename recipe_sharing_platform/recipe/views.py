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
from .forms import RecipeForm, NutritionalInformationForm,ProfileForm,IngredientForm,CategoryForm,CreateUserForm
import random
from django.db.models import Avg
from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail 

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
            if(user.email=="admin@gmail.com" and user.password=="Admin@123"):
                return redirect('admin_dashboard')
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
    recipes = Recipe.objects.all()  # Fetch all recipes
    #recipes = Recipe.objects.filter(status='approved') # only showing the recipes that are approved
    return render(request, 'recipe.html', {'recipes': recipes})

def about(request):
    return render(request, 'about.html' )
#ABOUT VIEW
def contact(request):
    return render(request, 'contact.html')

def addrecipe(request):
    if request.method == 'POST':
        recipename = request.POST.get('recipename')
        ingredients = request.POST.get('ingredients')
        instructions = request.POST.get('instructions')
        image = request.FILES.get('image')
        tags = request.POST.get('tags')
        category = request.POST.get('category')
        ratings = request.POST.get('ratings')

        # Handle nutritional information
        calories = request.POST.get('calories')
        protein = request.POST.get('protein')
        fat = request.POST.get('fat')
        carbohydrates = request.POST.get('carbohydrates')
        sugar = request.POST.get('sugar')
        fiber = request.POST.get('fiber')

        # Validate fields
        if not all([recipename, ingredients, instructions, image, tags, category, ratings, calories, protein, fat, carbohydrates, sugar, fiber]):
            return render(request, 'add_recipe.html', {
                'error': 'All fields are required!',
                'recipename': recipename,
                'ingredients': ingredients,
                'instructions': instructions,
                'tags': tags,
                'category': category,
                'ratings': ratings,
                'calories': calories,
                'protein': protein,
                'fat': fat,
                'carbohydrates': carbohydrates,
                'sugar': sugar,
                'fiber': fiber,
            })

        # Save Recipe
        recipe = Recipe.objects.create(
            recipename=recipename,
            ingredients=ingredients,
            instructions=instructions,
            image=image,
            tags=tags,
            category=category,
            ratings=ratings,
        )

        # Save Nutritional Information
        NutritionalInformation.objects.create(
            recipe=recipe,
            calories=calories,
            protein=protein,
            fat=fat,
            carbohydrates=carbohydrates,
            sugar=sugar,
            fiber=fiber,
        )

        return redirect('success_page')  # Redirect to a success page or recipe list

    return render(request, 'addrecipe.html')


def recipe_detail(request, id):
    recipe = Recipe.objects.get(id=id)
    average_rating = recipe.ratings.aggregate(Avg('rating'))['rating__avg']
    total_ratings = recipe.ratings.count()

    # Assuming nutritional info is related as well
    nutritional_info = recipe.nutritional_info

    context = {
        'recipe': recipe,
        'average_rating': average_rating,
        'total_ratings': total_ratings,
        'nutritional_info': nutritional_info,
    }
    return render(request, 'recipe_detail.html', context)

#for edting recipes on recipe page for user
def usereditrecipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    
    if request.method == 'POST':
        recipe_form = RecipeForm(request.POST, request.FILES, instance=recipe)
        nutritional_info_form = NutritionalInformationForm(request.POST, instance=recipe.nutritional_info)

        if recipe_form.is_valid() and nutritional_info_form.is_valid():
            recipe_form.save()
            nutritional_info_form.save()
            return redirect('recipe_detail', recipe.id)
    else:  # This 'else' needs to be aligned with the 'if' statement
        recipe_form = RecipeForm(instance=recipe)
        nutritional_info_form = NutritionalInformationForm(instance=recipe.nutritional_info)

    return render(request, 'usereditrecipe.html', {
        'recipe_form': recipe_form,
        'nutritional_info_form': nutritional_info_form,
        'recipe': recipe
    })

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


#RECIPE MANAGER DASHBOARD VIEW
def recipe_manager_dashboard(request):
    recipes = Recipe.objects.all() # List all recipes
    users = CustomUser.objects.all() # List all users
    #pending_recipes = Recipe.objects.filter(status='pending')  # List pending recipes
    context = {'recipes': recipes, 'users': users}##########
    return render(request, 'recipe_manager_dashboard.html',context)
#code for view_user in recipe manager dashboard

#code for add_recipe in recipe manager dashboard
def add_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('recipe_manager_dashboard')
    else:
        form = RecipeForm()
    category=Category.objects.all()
    return render(request, 'add_recipe.html', {'categories':category})

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

#def pending_recipes(request):
   # recipes = Recipe.objects.filter(status='pending')
  #  return render(request, 'pending_recipes.html', {'recipes': recipes})

#def approve_recipe(request, recipe_id):
 #   recipe = get_object_or_404(Recipe, id=recipe_id)
    #recipe.status = 'approved'
    #recipe.save()
    #messages.success(request, "Recipe approved successfully!")
    #return redirect('pending_recipes')

#def reject_recipe(request, recipe_id):
    #recipe = get_object_or_404(Recipe, id=recipe_id)
    #recipe.status = 'rejected'
   # recipe.save()
   # messages.success(request, "Recipe rejected successfully!")
   # return redirect('pending_recipes')  # Redirect to pending recipes view

# View to list all ingredients
def ingredient_list(request):
    ingredients = Ingredient.objects.all()
    return render(request, 'ingredient_list.html', {'ingredients': ingredients})


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
# def edit_ingredient(request, pk):
#     ingredient = get_object_or_404(Ingredient, pk=pk)
#     if request.method == 'POST':
#         form = IngredientForm(request.POST, instance=ingredient)
#         if form.is_valid():
#             form.save()
#             return redirect('ingredient_list')
#     else:
#         form = IngredientForm(instance=ingredient)
#     return render(request, 'edit_ingredient.html', {'form': form, 'ingredient': ingredient})

# def category_list(request):
#     categories = Category.objects.all()
#     return render(request, 'category_list.html', {'categories': categories})

# def add_category(request):
#     if request.method == "POST":
#         form = CategoryForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('category-list')  # Replace with your category list URL name
#     else:
#         form = CategoryForm()
#     return render(request, 'add_category.html', {'form': form})

# def edit_category(request, pk):
#     category = get_object_or_404(Category, pk=pk)
#     if request.method == "POST":
#         form = CategoryForm(request.POST, instance=category)
#         if form.is_valid():
#             form.save()
#             return redirect('category-list')  # Replace with your category list URL name
#     else:
#         form = CategoryForm(instance=category)
#     return render(request, 'edit_category.html', {'form': form})

# def delete_category(request, pk):
#     category = get_object_or_404(Category, pk=pk)
#     category.delete()
#     return redirect('category-list')  # Replace with your category list URL name

#########################################################
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
def review_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    review_text = request.POST.get('review')

    # Create a new review
    review = Review.objects.create(user=request.user, recipe=recipe, review_text=review_text)
    review.save()

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

####################################################
def get_ingredients(request, category_id):
    if request.method == 'GET':
        # Filter ingredients based on the category_id passed in the URL
        if category_id == 1:
            ingredients = Ingredient.objects.filter(category_id=category_id)
        else:
            ingredients = Ingredient.objects.all()
        ingredient_list = [{'id': ingredient.ingredient_id, 'name': ingredient.name} for ingredient in ingredients]
        return JsonResponse({'ingredients': ingredient_list})
    
def get_nutritional_info(request, ingredient_id):
    try:
        nutrient_info = NutritionalInformation.objects.get(id=ingredient_id)
        data = {
            'protein': nutrient_info.protein,
            'fiber': nutrient_info.fiber,
            'fat': nutrient_info.fat,
            'carbohydrates': nutrient_info.carbohydrates,
            'calories': nutrient_info.calories,
            'sugars': nutrient_info.sugars,
        }
        return JsonResponse(data)
    except NutritionalInformation.DoesNotExist:
        return JsonResponse({}, status=404)