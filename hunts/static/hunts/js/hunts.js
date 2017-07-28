function incorrect_answer(guess, timeout, new_hints, old_unlocks, new_unlocks) {
	var hints_div = $('#hints');
	var n_hints = new_hints.length;
	for (var i = 0; i < n_hints; i++) {
		hints_div.append('<p>' + new_hints[i].time + ': ' + new_hints[i].text + '</p>');
	}

	var unlocks_div = $('#unlocks');
	unlocks_div.empty();

	var n_unlocks = old_unlocks.length;
	for (var i = 0; i < n_unlocks; i++) {
		unlocks_div.append('<p>' + old_unlocks[i].guesses[0] + ' : ' + old_unlocks[i].text + '</p>');
	}
	var n_unlocks = new_unlocks.length;
	for (var i = 0; i < n_unlocks; i++) {
		var unlock_p = $('<p class="new-unlock">' + guess + ' : ' + new_unlocks[i] + '</p>');
		unlock_p.appendTo(unlocks_div);
	}

	var milliseconds = Date.parse(timeout) - Date.now();
	var answer_button = $('#answer-button');
	answer_button.after('<span id="answer-blocker"> You may guess again in 5 seconds.</span>');
	setTimeout(function () {
		answer_button.removeAttr('disabled');
		$('#answer-blocker').remove();
	}, milliseconds);
	answer_button.hide().delay(milliseconds).show(0);
}

function correct_answer(url) {
	var form = $('.form-inline');
	form.after('<div id="correct-answer-message">Correct! Taking you to the next puzzle. <a class="puzzle-complete-redirect" href="' + url + '">go right now</a></div>');
	form.remove();
	setTimeout(function () {window.location.href = url;}, 3000);
}

function message(message, error) {
	var error_msg = $('<p class="submission-error" title="' + error + '">' + message + '</p>');
	error_msg.appendTo($('.form-inline')).delay(5000).fadeOut(5000, function(){$(this).remove();})
}

var last_updated = Date.now();

$(function() {
	$('.form-inline').submit(function(e) {
		e.preventDefault();
		var form = $(e.target);
		var button = form.children('button');
		if (button.attr('disabled') == 'true') {
			return;
		}
		button.attr('disabled', 'true');
		var data = {
			last_updated: last_updated,
			answer: form.children('input[name=answer]')[0].value
		};
		$.ajax({
			type: 'POST',
			url: 'an',
			data: jQuery.param(data),
			contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
			success: function(data) {
				last_updated = Date.now();
				if (data.correct == "true") {
					button.removeAttr('disabled');
					correct_answer(data.url);
				} else {
					incorrect_answer(data.guess, data.timeout, data.new_hints, data.old_unlocks, data.new_unlocks);
				}
			},
			error: function(xhr, status, error) {
				button.removeAttr('disabled');
				if (xhr.responseJSON.error == "too fast") {
					message("Slow down there, sparky! You're supposed to wait 5s between submissions.", "");
				} else {
					message("There was an error submitting the answer.", error);
				}
			},
			dataType: 'json'
		});
	});
});
