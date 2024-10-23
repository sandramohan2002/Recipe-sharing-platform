from django.db import models

class Recipe(models.Model):
    # ... other fields ...
    servings = models.IntegerField()
    prep_time = models.IntegerField()
    cook_time = models.IntegerField()
    # ... other fields ...

