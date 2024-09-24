from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from .models import Recipe
from .models import NutritionalInformation

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email','password1', 'password2')

class RecipeForm(forms.ModelForm):    
    class Meta:
        model = Recipe
        fields = ['recipename', 'ingredients', 'instructions', 'image', 'tags', 'category', 'ratings', 'nutritional_info']  # Use 'nutritional_info'

class NutritionalInformationForm(forms.ModelForm):
    class Meta:
        model = NutritionalInformation
        fields = ['calories', 'protein', 'fat', 'carbohydrates', 'sugar', 'fiber']
        


