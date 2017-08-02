$(function(){
	$('#btnAddRasp').click(function(){
		
		$.ajax({
			url: '/addRaspberry',
			data: $('form').serialize(),
			type: 'POST',
			success: function(response){
				//console.log(response);
                alert("Raspberry ajouté !");
                window.location = "bluecap.herokuapp.com/showShowRaspberry";
			},
			error: function(error){
				console.log(error);
			}
		});
        
        //alert("test");
        
	});
});