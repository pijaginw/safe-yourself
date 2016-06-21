var result = 0;
var request;

window.addEventListener("load", function(){

		function checkPass() {
			var pass = $('#pass-name').val();
			request = $.ajax({
				url: 'http://194.29.146.156:9097/pijaginw/safeyourself/signup/validation',
				mimeType: 'application/json; charset=UTF-8',
				type: 'POST',
				data: pass,
				success: function(responseText, statusText, jqXHR) {

					result = responseText['entropy'];
					if (result > 2.2) {
						$('#hint').text( '' );
						$('#submitButton').attr("disabled", false);
					} else {
						$('#hint').text( 'password is too weak' );
						$('#submitButton').attr("disabled", true);
					}
				},
				error: function(jqXHR, statusText, errorThrown) {
					//alert(jqXHR.responseText);
				}
			});
		}

		elPassword = document.getElementById('pass-name');
		elPassword.addEventListener('input', checkPass, false);

}, false);