from django import forms
from recipes.models import *

ING_CHOICES = []
temp= []
ING_UNITS = (('cups','Cups'),('liters','Liters'),('tablespoons','Tablespoons'),('teaspoons','Teaspoons'),('pounds','Pounds'),('kilogram','Kilogram'))
# cursor.execute('SELECT id FROM recipes_ingredient WHERE  =' +ing_name)
# temp_id = cursor.fetchone()
for ing in Ingredient.objects.all():
	temp = [str(ing.id),str(ing.ingredient_name)]
	ING_CHOICES.append(temp)
print(ING_CHOICES)

class TestForm(forms.Form): # or forms.ModelForm
	test_name=forms.CharField(max_length=55)
	test_amount=forms.DecimalField(max_digits=5,decimal_places=2)
	test_unit=forms.CharField(max_length=15)

class AddRecipeForm(forms.ModelForm):
	class Meta:
		model = Recipe
		fields=('recipe_title','recipe_instructions','picture')

class AddRecipeFormIng(forms.Form):
	ingredient=forms.CharField(required=True,max_length=55)
	ingredient_amount=forms.DecimalField(required=True,max_digits=5,decimal_places=2)
	ingredient_unit=forms.ChoiceField(required=True,widget=forms.Select,choices=ING_UNITS)
	




class RecipeSearch(forms.Form):

	
	# ingredients= forms.ChoiceField(required=False,widget=forms.Select,choices=ING_CHOICES)
	ingredients= forms.ModelChoiceField(required=False,widget=forms.Select,queryset = Ingredient.objects.all(),empty_label='"Select Ingredient"')
	ingredient_amount=forms.DecimalField(required=False,max_digits=10,decimal_places=2)
	ingredient_unit=forms.ChoiceField(required=False,widget=forms.Select,choices=ING_UNITS)

class RecipeSearchTitle(forms.Form):
	recipe_title=forms.CharField(max_length=40)
