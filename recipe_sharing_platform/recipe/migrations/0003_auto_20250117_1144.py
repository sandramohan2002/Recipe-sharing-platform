# Generated by Django 3.2.25 on 2025-01-17 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0002_alter_rating_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='servings',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterModelTable(
            name='review',
            table='recipe_review',
        ),
    ]
