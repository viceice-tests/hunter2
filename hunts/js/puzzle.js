import '../scss/puzzle.scss';

import $ from 'jquery';
import * as d3 from "d3";

import { configureCSRF } from '../../hunter2/js/index.js';
import RobustWebSocket from 'robust-websocket';

function escapeHtml(text) {
	"use strict";
	return text.replace(/[\"&<>]/g, function (a) {
		return { '"': '&quot;', '&': '&amp;', '<': '&lt;', '>': '&gt;' }[a];
	});
}

function incorrect_answer(guess, timeout_length, timeout, new_hints, unlocks) {
	"use strict";
	var hints_div = $('#hints');
	var n_hints = new_hints.length;
	for (let i = 0; i < n_hints; i++) {
		hints_div.append('<p>' + new_hints[i].time + ': ' + new_hints[i].text + '</p>');
	}

	var milliseconds = Date.parse(timeout) - Date.now();
	var difference = timeout_length - milliseconds;

	// If the time the server is saying it will accept answers again is very different from our own
	// calculation of the same thing, assume that it's due to clock problems (rather than latency somewhere)
	// and just wait however long the server was trying to tell us.
	if (difference > 2000 || difference < 0) {
		message("Possible clock mismatch. Cooldown may be inaccurate.");
		milliseconds = timeout_length;
	}
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
	"use strict";
	if (!guesses.includes(content.guess_uid)) {
		var guesses_table = $('#guesses');
		guesses_table.append('<tr><td>' + content.by + '</td><td>' + content.guess + '</td><td>' + content.correct + '</td></tr>');
		guesses.push(content.guess_uid);
	}
}

var unlocks = {};

function updateUnlocks() {
	"use strict";
	var entries = Object.entries(unlocks);
	entries.sort(function (a, b) {
		if (a[1].unlock < b[1].unlock) return -1;
		else if(a[1].unlock > b[1].unlock) return 1;
		return 0;
	});
	var list = d3.select('#unlocks')
		.selectAll('p')
		.data(entries);
	list.enter()
		.append('p')
		.merge(list)
		.text(function (d, i) {
			return d[1].guesses.join(', ') + ': ' + d[1].unlock;
		});
	list.exit()
		.remove();
}

function receivedNewUnlock(content) {
	"use strict";
	if (!(content.unlock_uid in unlocks)) {
		unlocks[content.unlock_uid] = {'unlock': content.unlock, 'guesses': []};
	}
	if (!unlocks[content.unlock_uid].guesses.includes(content.guess)) {
		unlocks[content.unlock_uid].guesses.push(content.guess);
	}
	updateUnlocks();
}

function receivedChangeUnlock(content) {
	"use strict";
	if (!(content.unlock_uid in unlocks)) {
		console.log('WebSocket changed invalid unlock: ' + content.unlock_uid);
		return;
	}
	unlocks[content.unlock_uid].unlock = content.unlock;
	updateUnlocks();
}

function receivedDeleteUnlock(content) {
	"use strict";
	if (!(content.unlock_uid in unlocks)) {
		console.log('WebSocket deleted invalid unlock: ' + content.unlock_uid);
		return;
	}
	delete unlocks[content.unlock_uid];
	updateUnlocks();
}

function receivedDeleteUnlockGuess(content) {
	"use strict";
	if (!(content.unlock_uid in unlocks)) {
		console.log('WebSocket deleted guess for invalid unlock: ' + content.unlock_uid);
		return;
	}
	if (!(unlocks[content.unlock_uid].guesses.includes(content.guess))) {
		console.log('WebSocket deleted invalid guess (can happen if team made identical guesses): ' + content.guess);
		return;
	}
	var unlockguesses = unlocks[content.unlock_uid].guesses;
	var i = unlockguesses.indexOf(content.guess);
	unlockguesses.splice(i, 1);
	if (unlocks[content.unlock_uid].guesses.length == 0) {
		delete unlocks[content.unlock_uid];
	}
	updateUnlocks();
}

var hints = {};

function updateHints() {
	"use strict";
	var entries = Object.entries(hints);
	entries.sort(function (a, b) {
		if (a[1].time < b[1].time) return -1;
		else if(a[1].time > b[1].time) return 1;
		return 0;
	});
	var list = d3.select('#hints')
		.selectAll('p')
		.data(entries);
	list.enter()
		.append('p')
		.merge(list)
		.text(function (d, i) {
			return d[1].time + ': ' + d[1].hint;
		});
	list.exit()
		.remove();
}


function receivedNewHint(content) {
	"use strict";
	hints[content.hint_uid] = {'time': content.time, 'hint': content.hint};
	updateHints();
}

function receivedDeleteHint(content) {
	"use strict";
	if (!(content.hint_uid in hints)) {
		console.log('WebSocket deleted invalid hint: ' + content.hint_uid);
		return;
	}
	delete hints[content.hint_uid];
	updateHints();
}

function receivedError(content) {
	"use strict";
	console.log(content.error);
}

var socketHandlers = {
	'new_guess': receivedNewAnswer,
	'old_guess': receivedNewAnswer,
	'new_unlock': receivedNewUnlock,
	'old_unlock': receivedNewUnlock,
	'change_unlock': receivedChangeUnlock,
	'delete_unlock': receivedDeleteUnlock,
	'delete_unlockguess': receivedDeleteUnlockGuess,
	'new_hint': receivedNewHint,
	'delete_hint': receivedDeleteHint,
	'error': receivedError
};

var lastUpdated;

function openEventSocket(data) {
	"use strict";
	var ws_scheme = (window.location.protocol == "https:" ? "wss" : "ws") + '://';
	var sock = new RobustWebSocket(ws_scheme + window.location.host + '/ws' + window.location.pathname);
	sock.onmessage = function(e) {
		var data = JSON.parse(e.data);
		lastUpdated = Date.now();

		console.log(data);
		if (!(data.type in socketHandlers)) {
			console.log('Invalid message type ' + data.type);
			console.log(data.content);
		} else {
			var handler = socketHandlers[data.type];
			handler(data.content);
		}
	};
	sock.onerror = function(e) {
		message('Websocket is broken. You will not receive new information without refreshing the page.');
	};
	sock.onopen = function(e) {
		if (lastUpdated != undefined) {
			sock.send(JSON.stringify({'type': 'guesses-plz', 'from': lastUpdated}));
		} else {
			sock.send(JSON.stringify({'type': 'guesses-plz', 'from': 'all'}));
		}
		sock.send(JSON.stringify({'type': 'unlocks-plz'}));
	};
}

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

	$('.form-inline').submit(function(e) {
		e.preventDefault();
		var form = $(e.target);
		var button = form.children('button');
		if (button.attr('disabled') == true) {
			return;
		}
		button.attr('disabled', true);
		var data = {
			answer: field.val()
		};
		$.ajax({
			type: 'POST',
			url: 'an',
			data: $.param(data),
			contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
			success: function(data) {
				field.val('');
				fieldKeyup();
				if (data.correct == "true") {
					button.removeAttr('disabled');
					correct_answer(data.url, data.text);
				} else {
					incorrect_answer(data.guess, data.timeout_length, data.timeout_end, data.new_hints, data.unlocks);
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

document.addEventListener('DOMContentLoaded', function() {
  "use strict";
  var content = $('#soln-content');
  var button = $('#soln-button');

  content.on('show.bs.collapse', function() {
    var url = button.data('url');
    $('#soln-text').load(url);
    $(this).unbind('show.bs.collapse');
  });
  content.on('shown.bs.collapse', function() {
    button.text('Hide Solution');
  });
  content.on('hidden.bs.collapse', function() {
    button.text('Show Solution');
  });
});
