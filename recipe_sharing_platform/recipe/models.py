from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser



#class User(AbstractUser):
   # ROLE_CHOICES = [
       # ('admin', 'Admin'),
       ## ('recipe_manager', 'Recipe Manager'),
       # ('user', 'User'),
    ##]
   # role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

#class User(AbstractUser):
    #is_CustomUser=models.BooleanField(default=False)
    #is_RecipeManager=models.BooleanField(default=False)
class login(models.Model):
    login_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=30, unique=True)  # Ensure email is unique
    password = models.CharField(max_length=30)
    reset_token = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.username

#SIGNUP DATABASE DETAILS
class CustomUser(models.Model):
    #user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=255, null=False, blank=False)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    is_blocked = models.BooleanField(default=False)
    #profile_picture = models.ImageField(upload_to='profile_pics', null=True, blank=True)

    def __str__(self):
        return self.name
    
    #class RecipeManager(models.Model):


#RECIPE MODELS
class Recipe(models.Model):
    recipename = models.CharField(max_length=200, null=True)
    ingredients = models.TextField(max_length=700, null=True)
    instructions = models.TextField(null=True)
    image = models.ImageField(upload_to='recipes/', blank=True, null=True)
    tags = models.TextField(max_length=200, null=True)
    category = models.TextField(max_length=200, null=True)
    ratings = models.IntegerField()
    nutritional_info = models.OneToOneField('NutritionalInformation', on_delete=models.SET_NULL, null=True, blank=True, related_name='recipe_info')  # Change related_name
     
    def __str__(self):
        return self.recipename

#NUTRITIONAL INFORMATION MODELS
class NutritionalInformation(models.Model):
    recipe = models.OneToOneField('Recipe', on_delete=models.CASCADE, related_name='nutritional_info_link')  # Change related_name
    calories = models.FloatField(null=True, blank=True)
    protein = models.FloatField(null=True, blank=True)
    fat = models.FloatField(null=True, blank=True)
    carbohydrates = models.FloatField(null=True, blank=True)
    sugar = models.FloatField(null=True, blank=True)
    fiber = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Nutritional Info (Calories: {self.calories})"
