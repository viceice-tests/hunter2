function incorrect_answer(guess, timeout_length, timeout, new_hints, unlocks) {
	var hints_div = $('#hints');
	var n_hints = new_hints.length;
	for (var i = 0; i < n_hints; i++) {
		hints_div.append('<p>' + new_hints[i].time + ': ' + new_hints[i].text + '</p>');
	}

	var unlocks_div = $('#unlocks');
	unlocks_div.empty();

	var n_unlocks = unlocks.length;
	for (var i = 0; i < n_unlocks; i++) {
		guesses = unlocks[i].guesses.join(', ');
		if (unlocks[i].new) {
			unlocks_div.append('<p class="new-unlock">' + guesses + ': ' + unlocks[i].text + '</p>');
		} else {
			unlocks_div.append('<p>' + guesses + ': ' + unlocks[i].text + '</p>');
		}
	}

	var milliseconds = Date.parse(timeout) - Date.now();
	var difference = timeout_length - milliseconds;

	// If the time the server is saying it will accept answers again is very different from our own
	// calculation of the same thing, assume that it's due to clock problems (rather than latency somewhere)
	// and just wait however long the server was trying to tell us.
	if (difference > 2000 || difference < 0) {
		message("Your clock seems not to match the server's. The displayed cooldown may not be optimal.");
		milliseconds = timeout_length;
	}
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
				form.children('input[name=answer]')[0].value = ''
				last_updated = Date.now();
				if (data.correct == "true") {
					button.removeAttr('disabled');
					correct_answer(data.url);
				} else {
					incorrect_answer(data.guess, data.timeout_length, data.timeout_end, data.new_hints, data.unlocks);
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
