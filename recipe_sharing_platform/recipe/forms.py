from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from .models import Recipe
from .models import NutritionalInformation,Ingredient,Category
from .models import CustomUser

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email','password1', 'password2')

class RecipeForm(forms.ModelForm):    
    class Meta:
        model = Recipe
        fields = ['recipename', 'ingredients', 'instructions', 'image', 'tags', 'category_id']  # Include category_id instead of category
        widgets = {
            'recipename': forms.TextInput(attrs={'class': 'form-control'}),
            'ingredients': forms.SelectMultiple(attrs={'class': 'form-control'}),  # Assuming you want a dropdown for multiple ingredients
            'instructions': forms.Textarea(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control'}),
            'category_id': forms.NumberInput(attrs={'class': 'form-control'}),  # Adjusted to match the model
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
    
class NutritionalInformationForm(forms.ModelForm):
    class Meta:
        model = NutritionalInformation
        fields = ['calories', 'protein', 'fat', 'carbohydrates', 'sugar', 'fiber']
        widgets = {
            'calories': forms.NumberInput(attrs={'class': 'form-control'}),
            'protein': forms.NumberInput(attrs={'class': 'form-control'}),
            'fat': forms.NumberInput(attrs={'class': 'form-control'}),
            'carbohydrates': forms.NumberInput(attrs={'class': 'form-control'}),
            'sugar': forms.NumberInput(attrs={'class': 'form-control'}),
            'fiber': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['name', 'email'] 
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name', 'substitutions', 'category_id']  # Using category_id as per your model
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'substitutions': forms.Textarea(attrs={'class': 'form-control'}),
            'category_id': forms.NumberInput(attrs={'class': 'form-control'}),  # Using IntegerField
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

