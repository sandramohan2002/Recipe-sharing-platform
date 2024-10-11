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
    name = models.CharField(max_length=255, null=False, blank=False)  # User's name
    email = models.EmailField(unique=True)  # User's unique email
    password = models.CharField(max_length=128)  # User's password (hashed)
    is_blocked = models.BooleanField(default=False)  # Block status of user

    def __str__(self):
        return self.name  # Returns the name when object is printed
    
# CATEGORY OF RECIPES:
class Category(models.Model):
    category_id = models.AutoField(primary_key=True)  # Unique ID for the category
    name = models.CharField(max_length=100,unique=True)  # Name of the category

    def __str__(self):
        return self.name  # Returns the name of the category

# INGREDIENTS OF RECIPES:
class Ingredient(models.Model):

    ingredient_id = models.AutoField(primary_key=True)  # Unique ID for the ingredient
    name = models.CharField(max_length=255, unique=True)  # Name of the ingredient
    substitutions = models.TextField(blank=True)  # Possible substitutions for the ingredient
    category_id = models.IntegerField(null=True, blank=True) # Category ID for this ingredient
    def __str__(self):
        return self.name  # Returns the name of the ingredient


# RECIPE MODEL:
class Recipe(models.Model):
    recipe_id = models.AutoField(primary_key=True)  # This is likely your current primary key
    recipename = models.CharField(max_length=200)  # Name of the recipe
    ingredients = models.ManyToManyField(Ingredient)  # Many-to-many relation with ingredients
    instructions = models.TextField()  # Instructions for the recipe
    image = models.ImageField(upload_to='recipes/')  # Image of the recipe
    tags = models.TextField(max_length=200)  # Tags related to the recipe
    category_id = models.IntegerField()  # Category ID for this recipe
    nutritional_info_id = models.IntegerField(null=True, blank=True)  # Nutritional info ID
    def __str__(self):
        return self.recipename  # Returns the name of the recipe
        
# NUTRITIONAL INFORMATION OF RECIPE
class NutritionalInformation(models.Model):
    nutritional_info_id = models.AutoField(primary_key=True)  # Unique ID for nutritional info
    recipe_id = models.IntegerField()  # Recipe ID associated with this nutritional info
    calories = models.FloatField(null=True, blank=True)  # Calories in the recipe
    protein = models.FloatField(null=True, blank=True)  # Protein content
    fat = models.FloatField(null=True, blank=True)  # Fat content
    carbohydrates = models.FloatField(null=True, blank=True)  # Carbohydrates content
    sugar = models.FloatField(null=True, blank=True)  # Sugar content
    fiber = models.FloatField(null=True, blank=True)  # Fiber content
    def __str__(self):
        return f"Nutritional Info (Calories: {self.calories})"  # Description for nutritional info

# RATINGS MODEL
class Rating(models.Model):
    rating_id = models.AutoField(primary_key=True)  # Unique ID for the rating
    recipe_id = models.IntegerField()  # ID of the recipe being rated
    user_id = models.IntegerField()  # ID of the user who rated the recipe
    rating = models.IntegerField()  # Rating value (e.g., 1-5)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of when the rating was created

    class Meta:
        unique_together = ('recipe_id', 'user_id')  # Ensure unique rating per user and recipe
    def __str__(self):
        return f'User {self.user_id} rated Recipe {self.recipe_id} {self.rating}/5'  # Description for rating

# REVIEWS MODELS:
class Review(models.Model):
    review_id = models.AutoField(primary_key=True)  # Unique ID for the review
    recipe_id = models.IntegerField()  # ID of the recipe being reviewed
    user_id = models.IntegerField()  # ID of the user who wrote the review
    review_text = models.TextField()  # Text of the review
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of when the review was created
    def __str__(self):
        return f'User {self.user_id} reviewed Recipe {self.recipe_id}'  # Description for review

# COMMENT MODEL
class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)  # Unique ID for the comment
    review_id = models.IntegerField(null=True, blank=True)  # ID of the review this comment belongs to
    user_id = models.IntegerField()  # ID of the user making the comment
    comment_text = models.TextField()  # Text of the comment
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of when the comment was created
    def __str__(self):
        return f'User {self.user_id} commented: {self.comment_text[:20]}...'  # Description for comment
    

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    measurement = models.CharField(max_length=20)

    class Meta:
        unique_together = ('recipe', 'ingredient')

    def __str__(self):
        return f"{self.quantity} {self.measurement} of {self.ingredient.name} for {self.recipe.recipename}"

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()

    def __str__(self):
        return self.question