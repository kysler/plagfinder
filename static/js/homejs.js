/* global var1, var2 */

$(document).ready(function(){
	$('.scan').hide();
    $("#upload_link").on('click', function(e){
        e.preventDefault();
        $("#upload:hidden").trigger('click');
    });
	
        $("#upload_link2").on('click', function(e){
        e.preventDefault();
        $("#display:hidden").trigger('click');
    });
	
	$("#upload_link3").on('click', function(e){
        e.preventDefault();
        $("#display1:hidden").trigger('click');
    });
	
	
	
    $("#button0").on('click', function(e){
        e.preventDefault();
        $(".scan:hidden").trigger('click');
    });

});


