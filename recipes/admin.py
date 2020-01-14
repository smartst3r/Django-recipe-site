from django.contrib import admin
from .models import *

admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(Recipe_Ingredients)
# Register your models here.
