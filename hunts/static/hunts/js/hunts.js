function incorrect_answer(guess, timeout, new_unlocks) {
	var n_unlocks = new_unlocks.length;
	for (var i = 0; i < n_unlocks; i++) {
		$('#unlocks').append('<p>' + guess + ' : ' + new_unlocks[i] + '</p>');
	}
	seconds = Date.parse(timeout) - Date.now();
	answer_button = $('#answer-button');
	answer_button.after('<span id="answer-blocker"> You may guess again in 5 seconds.</span>');
	setTimeout(function () {$('#answer-blocker').remove();}, seconds);
	answer_button.hide().delay(seconds).show(0);
}

function correct_answer(url) {
	form = $('.form-inline');
	form.after('<div id="correct-answer-message">Correct! Taking you to the next puzzle. <a class="puzzle-complete-redirect" href="' + url + '">go right now</a></div>');
	form.remove();
	setTimeout(function () {window.location.href = url;}, 3000);
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
				if (data.correct == "true") {
					correct_answer(data.url);
				} else {
					incorrect_answer(data.guess, data.timeout, data.new_unlocks);
				}
			},
			error: function(xhr, status, error) {
				alert(status);
			},
			dataType: 'json'
		});
	});
});
