function incorrect_answer(guess, timeout, old_unlocks, new_unlocks) {
	var unlocks_div = $('#unlocks');
	unlocks_div.empty();

	var n_unlocks = old_unlocks.length;
	for (var i = 0; i < n_unlocks; i++) {
		unlocks_div.append('<p>' + old_unlocks[i].guesses[0] + ' : ' + old_unlocks[i].text + '</p>'); //.css('background-color', 'purple').animate({background-color: 'none'});
	}
	var n_unlocks = new_unlocks.length;
	for (var i = 0; i < n_unlocks; i++) {
		var unlock_p = $('<p class="new-unlock">' + guess + ' : ' + new_unlocks[i] + '</p>');
		//.css('background-color', 'yellow').animate({background-color: 'none'});
		unlock_p.appendTo(unlocks_div);
	}

	var milliseconds = Date.parse(timeout) - Date.now();
	var answer_button = $('#answer-button');
	answer_button.after('<span id="answer-blocker"> You may guess again in 5 seconds.</span>');
	setTimeout(function () {$('#answer-blocker').remove();}, milliseconds);
	answer_button.hide().delay(milliseconds).show(0);
}

function correct_answer(url) {
	var form = $('.form-inline');
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
					incorrect_answer(data.guess, data.timeout, data.old_unlocks, data.new_unlocks);
				}
			},
			error: function(xhr, status, error) {
				alert(status);
			},
			dataType: 'json'
		});
	});
});
