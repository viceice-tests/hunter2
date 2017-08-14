function incorrect_answer(guess, timeout, new_hints, unlocks) {
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
	var answer_button = $('#answer-button');
	doCooldown(milliseconds);
	answer_button.after('<span id="answer-blocker"> You may guess again in 5 seconds.</span>');
	setTimeout(function () {
		answer_button.removeAttr('disabled');
		$('#answer-blocker').remove();
	}, milliseconds);
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

function doCooldown(milliseconds) {
	var size = 100;

	var svg = d3.select("form.form-inline").insert("svg", "button + *");
	svg.attr("width", size).attr("height", size);
	var path = svg.append("path");
	path.attr("fill", "red");
	path.transition()
		.duration(milliseconds)
		.ease(d3.easeLinear)
		.attrTween("d", function () { return drawSliceSquare(size); });

	var text = svg.append("text")
		.attr("x", size / 2)
		.attr("y", size / 2)
		.attr("fill", "black")
		.attr("text-anchor", "middle")
		.attr("font-weight", "bold")
		.attr("font-size", 18);
	text.transition()
		.duration(milliseconds)
		.ease(d3.easeLinear)
		.tween("text", function () {
			console.log(this);
			var oldthis = this;
			return function (t) {
				var time = milliseconds * (1-t) / 1000;
				d3.select(oldthis).text(time < 1 ? d3.format(".1f")(time) : d3.format(".0f")(time));
			};
		});


	setTimeout(function () {
		svg.remove();
	}, milliseconds);
}

function drawSliceSquare(size) {
	return function(proportion) {
		angle = (proportion * Math.PI * 2) - Math.PI / 2;
		var x = Math.cos(angle) * size;
		var y = Math.sin(angle) * size;
		var pathString = "M " + size / 2 + ",0" +
						" L " + size / 2 + "," + size / 2 +
						" l " + x + "," + y;
		var pathEnd = " Z";
		if (proportion < 0.875) {
			pathEnd = " L 0,0 Z" + pathEnd;
		}
		if (proportion < 0.625) {
			pathEnd = " L 0," + size + pathEnd;
		}
		if (proportion < 0.375) {
			pathEnd = " L " + size + "," + size + pathEnd;
		}
		if (proportion < 0.125) {
			pathEnd = " L " + size + ",0" + pathEnd;
		}
		return pathString + pathEnd;
	};
}

function drawCooldownText(milliseconds) {
	return function(proportion) {
		var time = milliseconds * proportion / 1000;
		//console.log(time);
		d3.select(this).text(time < 1 ? d3.format(".1")(time) : d3.format("1")(time));
	};
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
					incorrect_answer(data.guess, data.timeout, data.new_hints, data.unlocks);
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
