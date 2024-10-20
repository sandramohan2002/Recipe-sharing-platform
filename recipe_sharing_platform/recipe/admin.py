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



@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
       list_display = ('name', 'category_id', 'get_category_name')
       list_filter = ('category_id',)
       search_fields = ('name', 'category_id')





