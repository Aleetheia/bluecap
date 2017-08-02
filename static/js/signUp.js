$(function(){
	$('#btnAddRasp').click(function(){
		
		$.ajax({
			url: '/addRaspberry',
			data: $('form').serialize(),
			type: 'POST',
			success: function(response){
				console.log(response);
			},
			error: function(error){
				console.log(error);
			}
		});
        
        alert("test");
        
	});
});