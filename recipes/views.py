from django.shortcuts import render, get_object_or_404,redirect
from django.views.generic import TemplateView,FormView,View
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils import timezone
from .forms import *
from recipes.models import *
from django.forms import formset_factory
from .convert import *
from django.db import connection
from django.contrib.auth import authenticate, login
from django.core.files.storage import FileSystemStorage
from django.db.models import Max, Min
from django.views import generic
# notes need to make the additems part into a functions for reuse

	
def recipe(request, id):
	recipe = get_object_or_404(Recipe, pk=id)
	
	#generating ingredient list using recipe id
	recipe_ingredients=Recipe_Ingredients.objects.all().filter(recipe_id=recipe.id)
	print('recipe ingredients query:',recipe_ingredients)
	ingredients_list=[]
	for ingredient in recipe_ingredients:
		print('ingredient set:',ingredient)
		ingredient_name=Ingredient.objects.get(id=ingredient.ingredient_id)
		ingredient_list=[]
		ingredient_list.append(ingredient_name.ingredient_name)
		ingredient_list.append(float(ingredient.ingredient_amount))
		ingredient_list.append(ingredient.ingredient_unit)
		ingredients_list.append(ingredient_list)
		
	
	
	return render(request, 'recipes/recipepage.html', {'recipe': recipe,'error_message': "You didn't select a recipe.",'ingredients_list':ingredients_list,})

class UserFormView(View):
	# form_class = UserForm
	# template_name = 'recipes/signup.html'
	
	# def get(self,request):
		# form = self.form_class(None)
		# return render(request, self.template_name,{'form':form})
	
	# def post(self,request):
		# form = self.form_class(request.POST)
		
		# if form.is_valid():
			# user = form.save(commit=False)
			# username = form.cleaned_data['username']
			# password = form.cleaned_data['password']
			# #how to change passwords
			# user.set_password(password)
			# user.save()
			
			# user = authenticate(username=username,password=password)
			
			# if user is not None:
				
				# if user.is_active:
					
					# login(request,user)
					# return redirect('../ajax')
	pass
		# return render(request, self.template_name,{'form':form})

def test(request):
	recipe_ordered_date= Recipe.objects.order_by('-pub_date')
	most_recent={}
	temp=[]
	count=0
	for recipe in recipe_ordered_date:
		count+=1
		temp.append(recipe)
		if count>5:
			break
	for recipe in temp:
		ingredients_list=[]
		r_info=[]
		# print('recipe query:',recipe)
		r_info.append(recipe.recipe_title)
		r_info.append(str(recipe.picture))
		most_recent[recipe.id]=r_info
	# print('Most recent:',most_recent)
	return render(request, 'recipes/test.html',{'data': most_recent})



def ajax(request):
	###This part is working pretty good now!
	# note need to make it stop at 20 forms right now it will add more then 20 but only accept 20
	extra_forms = 1
	AddRecipeFormIngSet = formset_factory(AddRecipeFormIng,can_delete=True, extra=extra_forms, max_num=20)
	message='nothing'
	
	###Don't know currently exactly how this part works but it works
	if request.method == 'POST':
		form = AddRecipeForm(request.POST, request.FILES)
		formset = AddRecipeFormIngSet(request.POST)
		
		###Checking if data in recipe form is good
		if form.is_valid():
			print('Recipe Form.is_valid',form.cleaned_data)
			
			###Checking if data in ingredient formset is good
			if formset.is_valid():
				print('ingredient formset.is_valid',formset.cleaned_data)
				
				###checking if picture is their
				if 'picture' in request.FILES:
					uploaded_picture= request.FILES['picture']
					
					###checking if picture size is too big -- change number in if statement to change max size allowed
					if uploaded_picture.size > 150000:
						
						###Repopulating recipe form
						initial = {'recipe_title': form.cleaned_data['recipe_title'] ,'recipe_instructions' : form.cleaned_data['recipe_instructions'] }
						form = AddRecipeForm(initial=initial)
						
						###Repopulating ingredient form
						formset = AddRecipeFormIngSet(initial=[{'ingredient':formset.cleaned_data[x]['ingredient'], 'ingredient_amount': formset.cleaned_data[x]['ingredient_amount'], 'ingredient_unit' : formset.cleaned_data[x]['ingredient_unit']} for x in range(len(formset.cleaned_data))])
						message='Picture file is to big please keep it below 15kb'
						return render(request, 'recipes/ajax.html', {'formset': formset,'form':form,'message':message})
						
					###Picture size was fine
					else:
						print('Picture is good size')
				
				###Will set default picture if the picture was not uploaded
				else: 
					uploaded_picture='recipe_image/default.jpg'
								
				###Creating recipe
				title=form.cleaned_data['recipe_title'].capitalize()
				instructions=form.cleaned_data['recipe_instructions']
				recipe_object= Recipe.objects.create(recipe_title=title,pub_date=timezone.now(),change_date=timezone.now(),recipe_instructions=instructions,picture=uploaded_picture)
					
				###cycling through ingredients and linking the ingredient to the recipe
				for i in formset.cleaned_data:
				
					###going to skip if Delete was checked
					if i['DELETE']:
						print("Found deleted checked")
						continue
						
					###pulling out data to easier varibles to understand
					ing_name=i['ingredient'].capitalize()
					ing_amount=i['ingredient_amount']
					ing_unit=i['ingredient_unit']
					cv=convert_to_munit(ing_amount,ing_unit)
					
					###Checking if ingredient is already in the Database
					try:
						temp_id=Ingredient.objects.get(ingredient_name=ing_name)
						
						###Found the Ingredient and using it later to link to recipe
						ingredient_object= Ingredient.objects.get(pk=str(temp_id.id))
					 
					###Didn't find the recipe so now going to create that ingredient in the Database
					except:
						ingredient_object= Ingredient.objects.create(ingredient_name=ing_name)
						
					###Creating bridge entry between recipe and ingredients 
					bridge_object= Recipe_Ingredients.objects.create(recipe=recipe_object,ingredient=ingredient_object,ingredient_amount=ing_amount,ingredient_unit=ing_unit,ingredient_convert=cv)
					
					###Saving everything!
					ingredient_object.save()
					bridge_object.save()
				recipe_object.save()
					
				###Redirect to recipe page, recipe was correctly entered
				print('Recipe was made correctly')
				return redirect('../'+str(recipe_object.id)+'')
			
			###Error message for ingredient formset
			else:
				print('ingredient formset is not valid')
				message='Ingredients were left empty please delete for remove'
		
		###Error message for recipe form
		else:
			print('something is not valid in recipe form')
			message='Either recipe title or instructions were left empty'
	
	###Don't know currently exactly how this part works but it works
	else:
		formset = AddRecipeFormIngSet()
		form = AddRecipeForm()
	return render(request, 'recipes/ajax.html', {'formset': formset,'form':form,'message':message})

def check(request):
	extra_forms1 = 1
	print('CHECK1')
	can_make_list={}
	RecipeSearchFormSet = formset_factory(RecipeSearch,can_delete=True, extra=extra_forms1, max_num=20)
	if request.method == 'POST':
		print('CHECK2')
		if request.is_ajax():
			
			formset = RecipeSearchFormSet(request.POST)
			print('CHECK3',formset.errors)
			if formset.is_valid():
				print('CHECK4')
				master_list={}
				ing_converted_list=[]
				final_list=[]
				

				
				for i in formset.cleaned_data:
					ing_id=i['ingredients']
					if i['DELETE']:
						print("deleted")
						continue
					try:
						ing_id=ing_id.id
					except:
						continue
					print('here')
					ing_amount=i['ingredient_amount']
					ing_unit=i['ingredient_unit']
					cu=convert_to_munit(ing_amount,ing_unit)
					master_list[ing_id]=cu
				print('Master list:',master_list)
				for key in master_list:
					
					recipe_list=Recipe_Ingredients.objects.all().filter(ingredient_id=key)
					for recipe in recipe_list:
						count=0
						print('Recipe id:',recipe.recipe_id)
						list_of_rows_with_recipe_id=Recipe_Ingredients.objects.all().filter(recipe_id=recipe.recipe_id)
						print(list_of_rows_with_recipe_id)
						for row in list_of_rows_with_recipe_id:
							print(list_of_rows_with_recipe_id.count())
							if list_of_rows_with_recipe_id.count() > len(master_list):
								continue
							try:
								if row.ingredient_convert <= master_list[int(row.ingredient_id)]:
									count+=1
									print(row.ingredient_convert," <= ",master_list[int(row.ingredient_id)])
							except:
								print('xd')
							print(list_of_rows_with_recipe_id.count(),count)
							if count==list_of_rows_with_recipe_id.count():
								print('gottem?')
								checked_recipe=Recipe.objects.get(id=row.recipe_id)
								r_info=[]
								ingredients_list=[]
								r_info.append(checked_recipe.recipe_title)
								r_info.append(str(checked_recipe.picture))
								r_info.append(str(checked_recipe.recipe_instructions))
								
								recipe_ingredients=Recipe_Ingredients.objects.all().filter(recipe_id=checked_recipe.id)
								for ingredient in recipe_ingredients:
									ingredient_name=Ingredient.objects.get(id=ingredient.ingredient_id)
									ingredient_list=[]
									ingredient_list.append(ingredient_name.ingredient_name)
									ingredient_list.append(float(ingredient.ingredient_amount))
									ingredient_list.append(ingredient.ingredient_unit)
									ingredients_list.append(ingredient_list)
								r_info.append(ingredients_list)
								print(r_info)
								can_make_list[checked_recipe.id]=r_info
							print('end')		
	
			return JsonResponse(can_make_list, safe=False)		
				
	else:
		formset = RecipeSearchFormSet()
	return render(request, 'recipes/check.html',{'wow':Ingredient.objects.all(),'formset':formset,'recipe_list':can_make_list})


































# class RecipeView(FormView):
	# form_class = AddRecipeForm
	# template_name = 'recipes/index.html'
	# success_url = '/form-success/'
	

	# def get(self,request):
		# r_form = AddRecipeForm(request.POST)
		
		
		# return render(request, self.template_name, {'r_form':r_form})

















def signup(request):
	
	return render(request, 'recipes/signup.html')
