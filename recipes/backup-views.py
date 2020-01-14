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
# notes need to make the additems part into a functions for reuse

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


	return render(request, 'recipes/test.html')

def ajax(request):
	# note need to make it stop at 20 forms right now it will add more then 20 but only accept 20
	extra_forms = 1
	AddRecipeFormIngSet = formset_factory(AddRecipeFormIng,can_delete=True, extra=extra_forms, max_num=20)
	
	# form = TestForm(request.POST)
	if request.method == 'POST':
		form = AddRecipeForm(request.POST, request.FILES)
		formset = AddRecipeFormIngSet(request.POST)
		if request.is_ajax():
			
			# print("HEELOOO")
			if form.is_valid():
				title=form.cleaned_data['recipe_title']
				instructions=form.cleaned_data['recipe_instructions']
				recipe_object= Recipe.objects.create(recipe_title=title,pub_date=timezone.now(),change_date=timezone.now(),recipe_instructions=instructions)
				recipe_object.save()
			else:
				print('something is not valid in forms')
			if formset.is_valid():
				print(formset.cleaned_data)
				for i in formset.cleaned_data:
					if i['DELETE']:
						print("deleted")
						continue
					print('\n',i['ingredient_name'],'\n')
					print('\n',i['ingredient_amount'],'\n')
					print('\n',i['ingredient_unit'],'\n')
					ing_name=i['ingredient_name']
					ing_amount=i['ingredient_amount']
					ing_unit=i['ingredient_unit']
					cv=convert_to_munit(ing_amount,ing_unit)
					ingredient_object= Ingredient.objects.create(ingredient_name=ing_name)
					bridge_object= Recipe_Ingredients.objects.create(recipe=recipe_object,ingredient=ingredient_object,ingredient_amount=ing_amount,ingredient_unit=ing_unit,ingredient_convert=cv)
					ingredient_object.save()
					bridge_object.save()
					
					data='Recipe Sucessfully Uploaded'
			else: 
				data='Recipe submitted had invalid data'
			return JsonResponse(data, safe=False)
					
	else:
		formset = AddRecipeFormIngSet()
		form = AddRecipeForm()
	return render(request, 'recipes/ajax.html', {'formset': formset,'form':form})

def get(request):
	# extra_forms = 1
	# AddRecipeFormSetIng = formset_factory(AddRecipeFormIng, extra=extra_forms, max_num=20)
	# form = AddRecipeForm(request.POST)
	# if request.method == 'POST':

			

		# if 'additems' in request.POST and request.POST['additems'] == 'true':
			# formset_dictionary_copy = request.POST.copy()
			# formset_dictionary_copy['form-TOTAL_FORMS'] =int(formset_dictionary_copy['form-TOTAL_FORMS']) + extra_forms
			# formset = AddRecipeFormSetIng(formset_dictionary_copy)
		
		# else:
			# formset = AddRecipeFormSetIng(request.POST)
			# if form.is_valid():
				# title=form.cleaned_data['recipe_title']
				# recipe_object= Recipe.objects.create(recipe_title=title,pub_date=timezone.now(),change_date=timezone.now())
				# recipe_object.save()
				# if formset.is_valid():
					# for i in formset.cleaned_data:
						
						# ing_name=i['ingredient_name']
						# ing_amount=i['ingredient_amount']
						# ing_unit=i['ingredient_unit']
						# cv=convert_to_munit(ing_amount,ing_unit)
						# ingredient_object= Ingredient.objects.create(ingredient_name=ing_name)
						# bridge_object= Recipe_Ingredients.objects.create(recipe=recipe_object,ingredient=ingredient_object,ingredient_amount=ing_amount,ingredient_unit=ing_unit,ingredient_convert=cv)
						# ingredient_object.save()
						# bridge_object.save()
	# else:
		# formset = AddRecipeFormSetIng()
	return render(request)#, 'recipes/index.html', {'formset': formset,'form':form})

def check(request):
	extra_forms1 = 1
	# print('CHECK')
	can_make_list={}
	RecipeSearchFormSet = formset_factory(RecipeSearch,can_delete=True, extra=extra_forms1, max_num=20)
	if request.method == 'POST':
		# print('CHECK')
		if request.is_ajax():
			# print('CHECK')
			formset = RecipeSearchFormSet(request.POST)
			if formset.is_valid():
				ing_id_list=[]
				ing_converted_list=[]
				final_list=[]
				count2=0
				cursor = connection.cursor()
				
				for i in formset.cleaned_data:
					ing_id=i['ingredients']
					ing_amount=i['ingredient_amount']
					ing_unit=i['ingredient_unit']
					cu=convert_to_munit(ing_amount,ing_unit)
					ing_id_list.append(str(ing_id))
					ing_converted_list.append(cu)
				#this is not a effectient way to do this
				for i in  range(0,len(ing_id_list)):
					
					cursor.execute('SELECT recipe_id FROM recipes_recipe_ingredients WHERE ingredient_id ='+ing_id_list[i])
					rec_id_list = cursor.fetchone()
					for rec_id in rec_id_list:
						cursor.execute('SELECT ingredient_id FROM recipes_recipe_ingredients WHERE recipe_id ='+str(rec_id))
						ing_id_sql_list = cursor.fetchone()
						count=0
						cursor.execute('SELECT count(ingredient_id) FROM recipes_recipe_ingredients WHERE recipe_id = '+str(rec_id))
						recipe_ingredients_amount = cursor.fetchone()[0]
				
						for ing_id in ing_id_sql_list:
							
							if str(ing_id) in ing_id_list:
								count+=1
								# print('matched an ing_id to recipe')
								
						if count == len(ing_id_sql_list):
							# print('check1',ing_id_list,len(ing_id_list))
							for numb in range(0,len(ing_id_sql_list)):
								# print('loop :',numb,": :",rec_id,": :")
								cursor.execute('SELECT ingredient_convert FROM recipes_recipe_ingredients WHERE recipe_id ='+str(rec_id)+' AND ingredient_id = '+str(ing_id_sql_list[numb]))
								ing_sql_converted = cursor.fetchone()[0]
								if ing_converted_list[numb] >= ing_sql_converted:
									final_list.append(rec_id)
									
									
						else:
							continue
							
							##fixed CHECK AROUND HERE TRY PRINT STATEMENST ITS NOT GETING TO THE END OF FUNCTION
						print('check')
						if amount_compare(cu,ing_sql_converted):
							count2+=1
							# print('xd')
							
							if count2==recipe_ingredients_amount:
								cursor.execute('SELECT recipe_title FROM recipes_recipe WHERE id ='+str(rec_id))
								recipe_name = cursor.fetchone()
								can_make_list[rec_id]=recipe_name
								print('HERER',can_make_list)
								count2=0
								
			
				
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
