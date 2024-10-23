import re
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from .models import Recipe, SubCategory
from .models import NutritionalInformation,Ingredient,Category
from .models import CustomUser

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email','password1', 'password2')

#Recipe Form
class RecipeForm(forms.ModelForm):
    category_id = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Select a category",
        to_field_name="category_id",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True  # Ensure category is required
    )
    subcategory_id = forms.ModelChoiceField(
        queryset=SubCategory.objects.none(),
        empty_label="Select a subcategory",
        required=False,
        to_field_name="subcategory_id",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Recipe
        fields = ['recipename', 'description', 'ingredients', 'instructions', 'image', 'servings', 'timing','tags', 'category_id', 'subcategory_id']
        widgets = {
            'recipename': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'ingredients': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'timing': forms.TimeInput(format='%H:%M'),  # Adjust the format if needed
        }

    # Custom validation for recipename
    def clean_recipename(self):
        recipename = self.cleaned_data.get('recipename')
        
        # Check if the recipe name has only spaces
        if not recipename.strip():
            raise forms.ValidationError("Recipe name cannot be empty or contain only spaces.")
        
        # Check if recipe name is less than 3 characters
        if len(recipename) < 3:
            raise forms.ValidationError("Recipe name must be at least 3 characters long.")
        
        # Regular expression to allow only alphabets and spaces, no special characters or digits
        if not re.match(r'^[A-Za-z\s]+$', recipename):
            raise forms.ValidationError("Recipe name cannot contain digits or special characters. Only letters and spaces are allowed.")
        
        return recipename

    # Custom validation for description (if required)
    def clean_description(self):
        description = self.cleaned_data.get('description')
        
        if not description.strip():
            raise forms.ValidationError("Description cannot be empty or contain only spaces.")
        
        return description

    # Custom validation for tags
    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        
        # Check if tags contain only spaces or is empty
        if not tags.strip():
            raise forms.ValidationError("Tags cannot be empty or contain only spaces.")
        
        # Regular expression to allow only alphabets and spaces, no special characters or digits
        if not re.match(r'^[A-Za-z\s,]+$', tags):  # Allowing commas for multiple tags
            raise forms.ValidationError("Tags cannot contain digits or special characters except commas. Only letters, spaces, and commas are allowed.")
        
        return tags

    # Custom validation for category (ensure it's selected)
    def clean_category_id(self):
        category_id = self.cleaned_data.get('category_id')
        
        # Ensure a category is selected
        if category_id is None:
            raise forms.ValidationError("Please select a valid category.")
        
        return category_id

    # Custom validation for image (ensure it's a valid image file)
    def clean_image(self):
        image = self.cleaned_data.get('image')
        
        # If image is required, check if it's present
        if not image:
            raise forms.ValidationError("Please upload an image for the recipe.")
        
        # Check if the uploaded file is an image
        if image and not image.content_type.startswith('image/'):
            raise forms.ValidationError("Please upload a valid image file.")
        
        return image

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'category_id' in self.data:
            try:
                category_id = int(self.data.get('category_id'))
                self.fields['subcategory_id'].queryset = SubCategory.objects.filter(category_id=category_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.category_id:
            self.fields['subcategory_id'].queryset = SubCategory.objects.filter(category_id=self.instance.category_id)

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if not image.name.lower().endswith(('png', 'jpg', 'jpeg')):
                raise forms.ValidationError("Image file must be in PNG, JPG, or JPEG format.")
        return image
    

#Nutritional Information Form
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



#Profile Form
class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['name', 'email'] 
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

#Ingredient Form
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
        

#Category Form
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

#Contact Form
class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your Message', 'rows': 5}), required=True)

#SubCategory Form
class SubCategoryForm(forms.ModelForm):
    category_id = forms.ChoiceField(choices=[], widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = SubCategory
        fields = ['category_id', 'name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category_id'].choices = [(c.category_id, c.name) for c in Category.objects.all()]