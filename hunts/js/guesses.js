import $ from 'jquery';
import 'bootstrap';

import '../scss/guesses.scss';

import setupJQueryAjaxCsrf from 'hunter2/js/csrf.js';

function updateGuesses(force) {
	"use strict";
	if (force || $('#auto-update').prop('checked')) {
		$('#guesses-container').load('guesses_content' + window.location.search + ' #guesses-container', function(data, status, req) {
			// Go for more guesses 5 seconds after we're done getting the last lot of guesses.
			setTimeout(updateGuesses, 5000);
		});
	}
}

function getQueryParam(param) {
	"use strict";
	var value;
	location.search.substr(1)
		.split("&")
		.some(function(item) { // returns first occurence and stops
			var keyAndValue = item.split("=");
			if (keyAndValue[0] == param) {
				value = keyAndValue[1];
				return true;
			} else {
				return false;
			}
		});
	return value;
}

$(function () {
	"use strict";

	setupJQueryAjaxCsrf();

	updateGuesses(true);
	var autoUpdate = $('#auto-update');
	var page = parseInt(getQueryParam('page'));
	if (page > 1) {
		autoUpdate.prop('checked', false);
	}
	autoUpdate.click(function (ev) {
		if ($(this).prop('checked')) {
			updateGuesses();
		}
	});
});
