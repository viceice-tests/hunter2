function lol() {
	alert("yes, lol.");
}

$(function() {
	$('.form-inline').submit(function(e) {
		e.preventDefault();
		var data = {
			answer: $('.form-inline input[name=answer]')[0].value
		};
		$.ajax({
			type: 'POST',
			url: 'an',
			data: jQuery.param(data),
			contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
			success: function(data) {
				lol();
			},
			error: function(xhr, status, error) {
				alert(status);
			},
			dataType: 'json'
		});
	});
});
