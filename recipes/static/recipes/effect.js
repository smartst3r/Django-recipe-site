$(document).ready(function(){
	$('<option>').click(function(){
	// $("ol").empty();
	var e = document.getElementById("m_ing");
	var value = e.options[e.selectedIndex].value;
	var texta = e.options[e.selectedIndex].text;
	console.log(value)
	
	$('#xd').append($('<li>',{
		text:'weffwe'
	}))
	
	;
});



})