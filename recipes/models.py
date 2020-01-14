from django.db import models

class Ingredient(models.Model):
	ingredient_name = models.CharField(max_length=55)
	
	def __str__(self):
		return self.ingredient_name

class Recipe(models.Model):
	recipe_title 		= models.CharField(max_length=55)
	pub_date     		= models.DateTimeField('date published')
	change_date  		= models.DateTimeField('date changed')
	recipe_instructions = models.TextField(max_length=1000)
	picture				= models.ImageField(upload_to='recipe_image', blank=True,null=True)
	ingredients  		= models.ManyToManyField(Ingredient, through='Recipe_Ingredients')

	def __str__(self):
		return self.recipe_title
	
class Recipe_Ingredients(models.Model):
	recipe            = models.ForeignKey(Recipe, on_delete=models.CASCADE)
	ingredient        = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
	ingredient_amount = models.DecimalField(max_digits=5,decimal_places=2)
	ingredient_unit   = models.CharField(max_length=15)
	ingredient_convert= models.DecimalField(max_digits=10,decimal_places=4)
	
	def __str__(self):
		return self.recipe.recipe_title+' :'+self.ingredient.ingredient_name
		
# class User(models.Model):
	# username = 
	# password = 
		
# Create your models here.
