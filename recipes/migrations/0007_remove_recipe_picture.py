# Generated by Django 2.1.5 on 2019-04-30 16:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_auto_20190430_1051'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='picture',
        ),
    ]
