$(function(){
	$('#btnSubmitRecipe').click(function(){
		
		$.ajax({
			url: '/addRecipe',
			data: $('form').serialize(),
			type: 'POST',
			success: function(response){
				console.log(response);
			},
			error: function(error){
				console.log(error);
			}
		});
	});
});