function escapeHtml(text) {
	"use strict";
	return text.replace(/[\"&<>]/g, function (a) {
		return { '"': '&quot;', '&': '&amp;', '<': '&lt;', '>': '&gt;' }[a];
	});
}

function incorrect_answer(guess, timeout, new_hints) {
	"use strict";
	var hints_div = $('#hints');
	var n_hints = new_hints.length;
	for (let i = 0; i < n_hints; i++) {
		hints_div.append('<p>' + new_hints[i].time + ': ' + new_hints[i].text + '</p>');
	}

	var milliseconds = Date.parse(timeout) - Date.now();
	var answer_button = $('#answer-button');
	doCooldown(milliseconds);
	setTimeout(function () {
		answer_button.removeAttr('disabled');
	}, milliseconds);
}

function correct_answer(url, text) {
	"use strict";
	var form = $('.form-inline');
	form.after(`<div id="correct-answer-message">Correct! Taking you ${text}. <a class="puzzle-complete-redirect" href="${url}">go right now</a></div>`);
	form.remove();
	setTimeout(function () {window.location.href = url;}, 3000);
}

function message(message, error) {
	"use strict";
	var error_msg = $('<p class="submission-error" title="' + error + '">' + message + '</p>');
	error_msg.appendTo($('.form-inline')).delay(5000).fadeOut(5000, function(){$(this).remove();});
}

function doCooldown(milliseconds) {
	"use strict";
	var button = d3.select("#answer-button");
	var size = button.node().getBoundingClientRect().width;
	var g = button.select("svg")
		.append("g");

	var path = g.append("path");
	path.attr("fill", "#33e")
		.attr("opacity", 0.9);

	var flashDuration = 150;
	path.transition()
		.duration(milliseconds)
		.ease(d3.easeLinear)
		.attrTween("d", function () { return drawSliceSquare(size); });

	setTimeout(function () {
		g.append("circle")
			.attr("cx", size / 2)
			.attr("cy", size / 2)
			.attr("r", 0)
			.attr("fill", "white")
			.attr("opacity", 0.95)
			.attr("stroke-width", 6)
			.attr("stroke", "white")
			.transition()
			.duration(flashDuration)
			.ease(d3.easeLinear)
			.attr("r", size / 2 * Math.SQRT2)
			.attr("fill-opacity", 0.3)
			.attr("stroke-opacity", 0.2);
	}, milliseconds - flashDuration);

	var text = g.append("text")
		.attr("x", size / 2)
		.attr("y", size / 2)
		.attr("fill", "white")
		.attr("text-anchor", "middle")
		.attr("font-weight", "bold")
		.attr("font-size", 22)
		.attr("dominant-baseline", "middle")
		.style("filter", "url(#drop-shadow)");

	text.transition()
		.duration(milliseconds)
		.ease(d3.easeLinear)
		.tween("text", function () {
			var oldthis = this;
			return function (t) {
				var time = milliseconds * (1-t) / 1000;
				d3.select(oldthis).text(time < 1 ? d3.format(".1f")(time) : d3.format(".0f")(time));
			};
		});

	setTimeout(function () {
		g.remove();
	}, milliseconds);
}

function drawSliceSquare(size) {
	"use strict";
	return function(proportion) {
		var angle = (proportion * Math.PI * 2) - Math.PI / 2;
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
	"use strict";
	return function(proportion) {
		var time = milliseconds * proportion / 1000;
		d3.select(this).text(time < 1 ? d3.format(".1")(time) : d3.format("1")(time));
	};
}

function drawFlashSquare(size) {
	"use strict";
	return function(t) {
		return "";
	};
}

function addSVG() {
	"use strict";
	var button = d3.select("#answer-button");
	var svg = button.append("svg");
	var size = button.node().getBoundingClientRect().width;
	svg.attr("width", size)
		.attr("height", size);

	var defs = svg.append("defs");

	/*var filter = defs.append("filter")
		.attr("id", "drop-shadow")
		.attr("x", "0")
		.attr("y", "0")
		.attr(*/
	var filter = defs.append("filter")
		.attr("id", "drop-shadow")
		.attr("width", "200%")
		.attr("height", "200%");
	filter.append("feGaussianBlur")
		.attr("in", "SourceAlpha")
		.attr("stdDeviation", 4)
		.attr("result", "blur");
	filter.append("feOffset")
		.attr("in", "blur")
		.attr("dx", 4)
		.attr("dy", 4)
		.attr("result", "offsetBlur");
	var feMerge = filter.append("feMerge");
	feMerge.append("feMergeNode")
		.attr("in", "offsetBlur");
	feMerge.append("feMergeNode")
		.attr("in", "SourceGraphic");
}

var guesses = [];

function receivedNewAnswer(content) {
	"use strict"
	if (!guesses.includes(content['timestamp'])) {
		var guesses_table = $('#guesses');
		guesses_table.append('<tr><td>' + content['by'] + '</td><td>' + content['guess'] + '</td><td>' + content['correct'] + '</td><td>' + content['unlocks'] + '</td></tr>');
		guesses.push(content['timestamp']);
	}
}

var unlocks = {};

function updateUnlocks() {
	"use strict"
	var entries = Object.entries(unlocks);
	entries.sort();
	var list = d3.select('#unlocks')
		.selectAll('p')
		.data(entries)
		.text(function (d, i) {
			return d[1].join(', ') + ': ' + d[0];
		})
		.enter()
		.append('p')
		.exit()
		.remove();
}

function receivedNewUnlock(content) {
	"use strict"
	if (!(content['unlock'] in unlocks)) {
		unlocks[content['unlock']] = [];
	}
	if (!unlocks[content['unlock']].includes(content['guess'])) {
		unlocks[content['unlock']].push(content['guess']);
	}
	updateUnlocks();
}

function openEventSocket(data) {
	"use strict";
	var ws_scheme = (window.location.protocol == "https:" ? "wss" : "ws") + '://';
	var sock = new WebSocket(ws_scheme + window.location.host + '/ws' + window.location.pathname);
	sock.onmessage = function(e) {
		var data = JSON.parse(e.data);
		if (data['type'] == 'new_guess' || data['type'] == 'old_guess') {
			receivedNewAnswer(data['content']);
		} else if (data['type'] == 'new_unlock' || data['type'] == 'old_unlock') {
			receivedNewUnlock(data['content']);
		} else if (data['type'] == 'error') {
			console.log(data['error']);
		} else {
			console.log('Invalid message type ' + data['type']);
			console.log(data['content']);
		}
	}
	sock.onerror = function(e) {
		message('Websocket is broken. You will not receive new information without refreshing the page.');
	}
	sock.onopen = function(e) {
		//sock.send(JSON.stringify({'type': 'unlocks-plz', 'from': 'all'}));
		//sock.send(JSON.stringify({'type': 'guesses-plz', 'from': 'all'}));
	};
}

var last_updated = Date.now();

$(function() {
	"use strict";
	addSVG();

	let field = $('#answer-entry');
	let button = $('#answer-button');

	function fieldKeyup() {
		if (!field.val()) {
			button.attr('disabled', true);
		} else {
			button.removeAttr('disabled');
		}
	}
	field.keyup(fieldKeyup);
	openEventSocket();
	/*$.ajax({
		type: 'GET',
		url: '/wsauth',
		success: openEventSocket,
		error: function(xhr, status, error) {
			message("Unable to authenticate for websocket. You will not get automatic updates.");
		},
		dataType: 'json'
	});*/

	$('.form-inline').submit(function(e) {
		e.preventDefault();
		var form = $(e.target);
		var button = form.children('button');
		if (button.attr('disabled') == true) {
			return;
		}
		button.attr('disabled', true);
		var data = {
			last_updated: last_updated,
			answer: field.val()
		};
		$.ajax({
			type: 'POST',
			url: 'an',
			data: jQuery.param(data),
			contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
			success: function(data) {
				field.val('');
				fieldKeyup();
				last_updated = Date.now();
				if (data.correct == "true") {
					button.removeAttr('disabled');
					correct_answer(data.url, data.text);
				} else {
					incorrect_answer(data.guess, data.timeout, data.new_hints);
				}
			},
			error: function(xhr, status, error) {
				button.removeAttr('disabled');
				if (xhr.responseJSON && xhr.responseJSON.error == "too fast") {
					message("Slow down there, sparky! You're supposed to wait 5s between submissions.", "");
				} else {
					message("There was an error submitting the answer.", error);
				}
			},
			dataType: 'json'
		});
	});
});
