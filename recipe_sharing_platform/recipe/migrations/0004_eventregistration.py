# Generated by Django 3.2.25 on 2025-01-25 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0003_auto_20250117_1144'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventRegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=10)),
                ('event', models.CharField(choices=[('italian', 'Italian Cuisine Workshop'), ('bread', 'Bread Making Masterclass'), ('photography', 'Food Photography Session')], max_length=20)),
                ('registration_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
