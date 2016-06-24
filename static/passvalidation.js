function checkPass(passId, buttonId) {
	var pass = $('#' + passId).val();
	request = $.ajax({
		url: '/pijaginw/safeyourself/signup/validation',
		mimeType: 'application/json; charset=UTF-8',
		type: 'POST',
		dataType: 'json',
		data: { pass : $('#' + passId).val() },
		success: function(responseText, statusText, jqXHR) {

			result = responseText['value'];
			if (result == 'OK') {
				$('#hint').text( '' );
				$('#' + buttonId).attr("disabled", false);
			} else {
				$('#hint').text( 'password is too weak!' );
				$('#' + buttonId).attr("disabled", true);
			}
		},
		error: function(jqXHR, statusText, errorThrown) {
			//alert(jqXHR.responseText);
		}
	});
}