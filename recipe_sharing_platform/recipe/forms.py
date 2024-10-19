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
        fields = ['recipename','description', 'ingredients', 'instructions', 'image', 'tags', 'category_id']  # Include category_id instead of category
        widgets = {
            'recipename': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'ingredients': forms.SelectMultiple(attrs={'class': 'form-control'}),  # Assuming you want a dropdown for multiple ingredients
            'instructions': forms.Textarea(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control'}),
            'category_id': forms.NumberInput(attrs={'class': 'form-control'}),  # Adjusted to match the model
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if not image.name.endswith(('png', 'jpg', 'jpeg')):
                raise forms.ValidationError("Image file must be in PNG, JPG, or JPEG format.")
        return image
    
class NutritionalInformationForm(forms.ModelForm):
    class Meta:
        model = NutritionalInformation
        fields = ['calories', 'protein', 'fat', 'carbohydrates', 'sugar', 'fiber']
        widgets = {
            'calories': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'protein': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'fat': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'carbohydrates': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'sugar': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'fiber': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
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
        fields = ['name', 'substitutions', 'category_id']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'substitutions': forms.TextInput(attrs={'class': 'form-control'}),
            'category_id': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_substitutions(self):
        data = self.cleaned_data.get('substitutions')
        if data and len(data) < 3:
            raise forms.ValidationError("Substitution should be at least 3 characters long.")
        return data
        

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')

        # Validate that the category name is not blank
        if not name:
            raise forms.ValidationError("Category name cannot be blank.")
        
        # Check for a minimum length (for example, 3 characters)
        if len(name) < 3:
            raise forms.ValidationError("Category name must be at least 3 characters long.")
        
        # Ensure the category name does not contain any special characters
        if not name.isalnum():
            raise forms.ValidationError("Category name should only contain letters and numbers.")

        return name



class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your Message', 'rows': 5}), required=True)
