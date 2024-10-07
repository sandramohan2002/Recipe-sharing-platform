from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(CustomUser)
admin.site.register(Recipe)
admin.site.register(NutritionalInformation)
admin.site.register(Ingredient)
admin.site.register(Category)
admin.site.register(Rating)
admin.site.register(Review)
admin.site.register(Comment)





