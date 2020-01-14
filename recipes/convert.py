unit_conv_dic = {'cups':.2365,'liters':1,'tablespoons':.0147,'teaspoons':.0049,'pounds':.4535,'kilogram':1}
def convert_to_munit(ing_amount,ing_unit):
	if ing_unit in unit_conv_dic:
		conv_value=unit_conv_dic[ing_unit]*float(ing_amount)
	else:
		conv_value='error unit not in unit list'
	return conv_value
		
		
def amount_compare(search_amount_converted,recipe_amount_converted):
	if float(search_amount_converted) >= float(recipe_amount_converted):
		t_f = True
	else:
		t_f = False
	return t_f
	
