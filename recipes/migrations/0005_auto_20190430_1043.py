# Generated by Django 2.1.5 on 2019-04-30 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_recipe_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='picture',
            field=models.ImageField(default=1, upload_to=''),
            preserve_default=False,
        ),
    ]
