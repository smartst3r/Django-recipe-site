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
from django.db.models import Max
from django.views import generic
from django.db.models import Min
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
	# note need to make it stop at 20 forms right now it will add more then 20 but only accept 20
	extra_forms = 1
	AddRecipeFormIngSet = formset_factory(AddRecipeFormIng,can_delete=True, extra=extra_forms, max_num=20)
	message='nothing'
	if request.method == 'POST':
		form = AddRecipeForm(request.POST, request.FILES)
		formset = AddRecipeFormIngSet(request.POST)
		if request.method== 'POST':
			if 'picture' in request.FILES:
				uploaded_picture= request.FILES['picture']
				# change the value in the if statement below to change max picture size allowed
				if uploaded_picture.size > 150000:
					formset = AddRecipeFormIngSet()
					form = AddRecipeForm()
					message='Picture file is to big please keep it below 15kb'
					return render(request, 'recipes/ajax.html', {'formset': formset,'form':form,'message':message})
				print(uploaded_picture)
				print(uploaded_picture.name)
				print(uploaded_picture.size)
			else: 
				uploaded_picture='recipe_image/default.jpg'
			

			if form.is_valid():
				title=form.cleaned_data['recipe_title'].capitalize()
				instructions=form.cleaned_data['recipe_instructions']
				recipe_object= Recipe.objects.create(recipe_title=title,pub_date=timezone.now(),change_date=timezone.now(),recipe_instructions=instructions,picture=uploaded_picture)
				
			else:
				print('something is not valid in forms')
			if formset.is_valid():
				cursor = connection.cursor()
				print(formset.cleaned_data)
				for i in formset.cleaned_data:
					if i['DELETE']:
						print("deleted")
						continue
					# print('\n',i['ingredient_name'],'\n')
					# print('\n',i['ingredient_amount'],'\n')
					# print('\n',i['ingredient_unit'],'\n')

					ing_name=i['ingredient'].capitalize()
					ing_amount=i['ingredient_amount']
					ing_unit=i['ingredient_unit']
					cv=convert_to_munit(ing_amount,ing_unit)
					try:
						temp_id=Ingredient.objects.get(ingredient_name=ing_name)
					# cursor.execute('SELECT id FROM recipes_ingredient WHERE  =' +ing_name)
					# temp_id = cursor.fetchone()
						print("HERE",temp_id.id)
					except:
						temp_id = 0
						print('xd',temp_id)
					if temp_id != 0 :
						ingredient_object= Ingredient.objects.get(pk=str(temp_id.id))
						print('wow here')
					else:
						ingredient_object= Ingredient.objects.create(ingredient_name=ing_name)
						ingredient_object.save()
					bridge_object= Recipe_Ingredients.objects.create(recipe=recipe_object,ingredient=ingredient_object,ingredient_amount=ing_amount,ingredient_unit=ing_unit,ingredient_convert=cv)
					bridge_object.save()
					
				recipe_object.save()
				# message='Recipe Sucessfully Uploaded'
				# data='Recipe Sucessfully Uploaded'
				return redirect('../'+str(recipe_object.id)+'')
			else: 
				pass
				# data='Recipe submitted had invalid data'
			
					
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
