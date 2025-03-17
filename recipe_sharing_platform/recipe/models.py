from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

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
    DIET_CHOICES = [
        ('veg', 'Vegetarian'),
        ('non_veg', 'Non-Vegetarian'), 
        ('vegan', 'Vegan'),
        ('pescatarian', 'Pescatarian'),
        ('other', 'Other')
    ]

    name = models.CharField(max_length=255, null=False, blank=False)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)  # Only one address field
    diet_preference = models.CharField(max_length=20, choices=DIET_CHOICES, default='other')
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    cooking_experience = models.CharField(max_length=50, blank=True, null=True)
    favorite_cuisine = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    is_blocked = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name  # Returns the name when object is printed
    
# CATEGORY OF RECIPES:
class Category(models.Model):
    category_id = models.AutoField(primary_key=True)  # Unique ID for the category
    name = models.CharField(max_length=100,unique=True)  # Name of the category
    status=models.BooleanField(default=False)
    def __str__(self):
        return self.name  # Returns the name of the category
    


class SubCategory(models.Model):
    subcategory_id = models.AutoField(primary_key=True)  # Unique ID for the subcategory
    category_id = models.IntegerField()  # Store the category ID as an integer
    name = models.CharField(max_length=100)  # Name of the subcategory
    class Meta:
        verbose_name_plural = "Subcategories"
        unique_together = ['category_id', 'name']  # Ensure subcategory names are unique within a category

    def __str__(self):
        return f"{self.name} (Category ID: {self.category_id})"

    def get_category_name(self):
        # You might want to implement a method to fetch the category name
        # This would require querying the Category model
        from .models import Category  # Import here to avoid circular import
        try:
            category = Category.objects.get(category_id=self.category_id)
            return category.name
        except Category.DoesNotExist:
            return "Unknown Category"

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
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard')
    ]
    
    user_id=models.IntegerField()
    recipe_id = models.AutoField(primary_key=True)  # This is likely your current primary key
    recipename = models.CharField(max_length=200)  # Name of the recipe
    description=models.TextField(max_length=200,null=True, blank=True)
    ingredients = models.ManyToManyField(Ingredient)  # Many-to-many relation with ingredients
    instructions = models.TextField()  # Instructions for the recipe
    image = models.ImageField(upload_to='recipes/')  # Image of the recipe
    servings = models.CharField(max_length=200)  # Add servings field
    prep_time = models.IntegerField()
    cook_time = models.IntegerField()
    timing = models.DurationField(null=True, blank=True)  # Add timing field
    tags = models.TextField(max_length=200)  # Tags related to the recipe
    category_id = models.IntegerField()  # Category ID for this recipe
    subcategory_id = models.IntegerField(null=True)
    nutritional_info_id = models.IntegerField(null=True, blank=True)  # Nutritional info ID
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='medium',
        null=True,  # Allow null for existing recipes
        blank=True  # Allow blank in forms
    )
    image_category = models.CharField(max_length=50, blank=True, null=True)
    category_confidence = models.FloatField(null=True, blank=True)
    def __str__(self):
        return self.recipename  # Returns the name of the recipe
        
# NUTRITIONAL INFORMATION OF RECIPE
class NutritionalInformation(models.Model):
    nutritional_id = models.AutoField(primary_key=True)
    recipe = models.OneToOneField(
        Recipe,
        on_delete=models.CASCADE,
        related_name='nutritional_info',
        db_column='recipe_id',
        null=True  # Temporarily allow null
    )
    calories = models.FloatField(default=0)
    protein = models.FloatField(default=0)
    carbohydrates = models.FloatField(default=0)
    fat = models.FloatField(default=0)
    fiber = models.FloatField(default=0)
    sugar = models.FloatField(default=0)
    is_ai_generated = models.BooleanField(default=False)

    class Meta:
        db_table = 'nutritional_information'

    def __str__(self):
        return f"Nutrition for {self.recipe.recipename if self.recipe else 'Unknown Recipe'}"

# RATINGS MODEL           ####OLD CODE######
# class Rating(models.Model):
#     rating_id = models.AutoField(primary_key=True)  # Unique ID for the rating
#     recipe_id = models.IntegerField()  # ID of the recipe being rated
#     user_id = models.IntegerField()  # ID of the user who rated the recipe
#     rating = models.IntegerField()  # Rating value (e.g., 1-5)
#     created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of when the rating was created

#     class Meta:
#         unique_together = ('recipe_id', 'user_id')  # Ensure unique rating per user and recipe
#     def __str__(self):
#         return f'User {self.user_id} rated Recipe {self.recipe_id} {self.rating}/5'  # Description for rating
# RATINGS MODEL
class Rating(models.Model):
    rating_id = models.AutoField(primary_key=True)
    recipe_id = models.IntegerField()
    user_id = models.IntegerField()
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # 1-5 rating
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('recipe_id', 'user_id')  # One rating per user per recipe

    def __str__(self):
        return f'User {self.user_id} rated Recipe {self.recipe_id} {self.rating}/5'

# # REVIEWS MODELS:      ####OLD CODE######
# class Review(models.Model):
#     review_id = models.AutoField(primary_key=True)  # Unique ID for the review
#     recipe_id = models.IntegerField()  # ID of the recipe being reviewed
#     user_id = models.IntegerField()  # ID of the user who wrote the review
#     review_text = models.TextField()  # Text of the review
#     created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of when the review was created
#     def __str__(self):
#         return f'User {self.user_id} reviewed Recipe {self.recipe_id}'  # Description for review
# REVIEWS MODEL
class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    recipe_id = models.IntegerField()
    user_id = models.IntegerField()
    #rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # 1-5 rating
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'recipe_review'

    def __str__(self):
        return f'User {self.user_id} reviewed Recipe {self.recipe_id}'
    
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

class EventRegistration(models.Model):
    # EVENT_CHOICES = [
    #     ('italian', 'Italian Cuisine Workshop'),
    #     ('bread', 'Bread Making Masterclass'),
    #     ('photography', 'Food Photography Session'),
    # ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=10)
    event = models.CharField(max_length=20)
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.get_event_display()}"

class Favorite(models.Model):
    user_id = models.IntegerField()  # Instead of ForeignKey to CustomUser
    recipe_id = models.IntegerField()  # Instead of ForeignKey to Recipe
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user_id', 'recipe_id']
        db_table = 'recipe_favorites'  # Optional: specify table name

    def __str__(self):
        try:
            user = CustomUser.objects.get(id=self.user_id)
            recipe = Recipe.objects.get(recipe_id=self.recipe_id)
            return f"{user.name} favorited {recipe.recipename}"
        except (CustomUser.DoesNotExist, Recipe.DoesNotExist):
            return f"Favorite {self.id}"

class RecipeAllergen(models.Model):
    recipe_id = models.IntegerField()  # This is the field we need to use
    allergen_name = models.CharField(max_length=50, choices=[
        ('dairy', 'Dairy'),
        ('eggs', 'Eggs'),
        ('nuts', 'Tree Nuts'),
        ('peanuts', 'Peanuts'),
        ('shellfish', 'Shellfish'),
        ('wheat', 'Wheat'),
        ('soy', 'Soy'),
        ('fish', 'Fish'),
        ('gluten', 'Gluten'),
        ('sesame', 'Sesame')
    ])
    severity = models.CharField(max_length=20, choices=[
        ('contains', 'Contains'),
        ('may_contain', 'May Contain'),
        ('traces', 'Traces')
    ])
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'recipe_allergens'
        unique_together = ['recipe_id', 'allergen_name']

    def __str__(self):
        return f"{self.get_allergen_name_display()} - {self.get_severity_display()}"

class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(
        max_length=50, 
        choices=[
            ('cooking_class', 'Cooking Class'),
            ('workshop', 'Workshop'),
            ('tasting', 'Food Tasting'),
            ('competition', 'Cooking Competition'),
            ('seminar', 'Culinary Seminar')
        ],
        default='workshop'
    )
    event_date = models.DateField()
    event_time = models.TimeField()
    location = models.CharField(max_length=200)
    max_participants = models.IntegerField(default=10)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    contact_email = models.EmailField(default='example@email.com')
    contact_phone = models.CharField(max_length=15, default='1234567890')
    duration_hours = models.IntegerField(default=1)
    duration_minutes = models.IntegerField(default=0)
    
    # Make instructor fields nullable
    instructor_name = models.CharField(max_length=200, null=True, blank=True)
    instructor_bio = models.TextField(null=True, blank=True)
    prerequisites = models.TextField(null=True, blank=True)
    schedule = models.TextField(null=True, blank=True)
    
    image = models.ImageField(upload_to='events/', null=True, blank=True)
    current_participants = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20, 
        choices=[
            ('upcoming', 'Upcoming'),
            ('ongoing', 'Ongoing'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled')
        ],
        default='upcoming'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'events'
        ordering = ['event_date', 'event_time']

    def __str__(self):
        return self.title

class MealPlan(models.Model):
    user_id = models.IntegerField()
    plan_date = models.DateField()
    meal_type = models.CharField(max_length=20)  # breakfast, lunch, dinner, snack
    recipe_details = models.JSONField()  # Store recipe info as JSON
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'meal_plan'

class DietaryTracking(models.Model):
    user_id = models.IntegerField()
    tracking_date = models.DateField()
    total_calories = models.FloatField(default=0)
    total_protein = models.FloatField(default=0)
    total_carbs = models.FloatField(default=0)
    total_fat = models.FloatField(default=0)
    water_intake = models.FloatField(default=0)  # in liters
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'dietary_tracking'

class DietaryGuideline(models.Model):
    CONDITION_CHOICES = [
        ('diabetic', 'Diabetic'),
        ('cholesterol', 'High Cholesterol'),
        ('blood_pressure', 'High Blood Pressure'),
        ('heart_disease', 'Heart Disease'),
        ('kidney_disease', 'Kidney Disease'),
        ('celiac', 'Celiac Disease'),
    ]

    condition = models.CharField(max_length=50, choices=CONDITION_CHOICES)
    nutrient = models.CharField(max_length=50)  # e.g., carbohydrates, fat, sugar, sodium
    min_value = models.FloatField()
    max_value = models.FloatField()
    unit = models.CharField(max_length=10)  # e.g., g, mg
    description = models.TextField()
    recommendations = models.TextField()

    class Meta:
        unique_together = ['condition', 'nutrient']

    def __str__(self):
        return f"{self.get_condition_display()} - {self.nutrient}"

class SubscriptionPlan(models.Model):
    DURATION_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES)
    features = models.JSONField()  # Store features as JSON
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.get_duration_display()}"

class UserSubscription(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired')
    ])
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_subscriptions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.name}'s subscription - {self.status}"

class PaymentHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    subscription = models.ForeignKey(UserSubscription, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed')
    ])
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100)
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payment_history'
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.status}"

    

