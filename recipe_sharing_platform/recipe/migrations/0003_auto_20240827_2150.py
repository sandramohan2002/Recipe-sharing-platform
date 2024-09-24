from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0002_auto_20240822_2214'),
    ]

    operations = [
        # Commenting out the CreateModel operation for Recipe
        # migrations.CreateModel(
        #     name='Recipe',
        #     fields=[
        #         ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #         ('recipename', models.CharField(max_length=200, null=True)),
        #         ('ingredients', models.TextField(max_length=200, null=True)),
        #         ('instructions', models.TextField(max_length=200, null=True)),
        #         ('image', models.ImageField(upload_to='\\media')),
        #         ('tags', models.TextField(max_length=200, null=True)),
        #         ('nutritionalInfo', models.TextField(max_length=200, null=True)),
        #         ('category', models.TextField(max_length=200, null=True)),
        #         ('ratings', models.IntegerField()),
        #     ],
        # ),
        migrations.AddField(
            model_name='customuser',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pics'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='mobile',
            field=models.IntegerField(unique=True),
        ),
    ]
