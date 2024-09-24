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
from .models import Recipe, NutritionalInformation
from .forms import RecipeForm, NutritionalInformationForm
import random
from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail

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
            
            # Directly compare plain text passwords
            if user.password == password:
                # request.session['user_id'] = user.id
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
    #logout(request)
    return redirect('login')
   



@login_required(login_url='login')
def homepage(request):
    return render(request, 'homepage.html')

@login_required(login_url='login')
def recipe(request):
    recipes = Recipe.objects.all()  # Fetch all recipes
    return render(request, 'recipe.html', {'recipes': recipes})




def about(request):
    return render(request, 'about.html')

@login_required(login_url='login')
def contact(request):
    return render(request, 'contact.html')

@login_required(login_url='login')
def addrecipe(request):
    if request.method == 'POST':
        recipe_form = RecipeForm(request.POST, request.FILES)
        nutritional_info_form = NutritionalInformationForm(request.POST)

        if recipe_form.is_valid() and nutritional_info_form.is_valid():
            recipe = recipe_form.save()  # Save the recipe first
            nutritional_info = nutritional_info_form.save(commit=False)  # Do not save yet
            nutritional_info.recipe = recipe  # Link it to the recipe
            nutritional_info.save()  # Now save the nutritional info

            messages.success(request, 'Recipe added successfully!')
            return redirect('recipe_detail', recipe_id=recipe.id)
    else:
        recipe_form = RecipeForm()
        nutritional_info_form = NutritionalInformationForm()

    return render(request, 'addrecipe.html', {
        'recipe_form': recipe_form,
        'nutritional_info_form': nutritional_info_form,
    })



def recipe_detail(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    nutritional_info = recipe.nutritional_info  # Accessing related nutritional info
    context = {
        'recipe': recipe,
        'nutritional_info': nutritional_info,
    }
    #return render(request, 'recipe.html', context)
    return render(request, 'recipe_detail.html', {'recipe': recipe})

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



def profile_view(request):
    # Your view logic here
    return render(request, 'profile.html')

# Admin dashboard view
#@login_required(login_url='login')
@login_required(login_url='login')
def admin_dashboard(request):
    recipes = Recipe.objects.all() # List all recipes
    users = CustomUser.objects.all() # List all users
    context = {'recipes': recipes, 'users': users}
    return render(request, 'admin_dashboard.html', context)
#recipe_manager_dashboard
def recipe_manager_dashboard(request):
    return render(request, 'recipe_manager_dashboard.html')


@login_required(login_url='login')
def add_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = RecipeForm()
    return render(request, 'add_recipe.html', {'form': form})

#code for edit_recipe in admin dashboard
@login_required(login_url='login')
def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = RecipeForm(instance=recipe)
    return render(request, 'edit_recipe.html', {'form': form, 'recipe': recipe})

#code for delete_recipe in admin dashboard
@login_required(login_url='login')
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    recipe.delete()
    return redirect('admin_dashboard')
    #return render(request, 'admin_dashboard.html')

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

