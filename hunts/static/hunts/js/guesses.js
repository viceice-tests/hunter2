function updateGuesses(force) {
	"use strict";
	if (force || $('#auto-update').prop('checked')) {
		$('#fill-me-up-you-slut').load('guesses_content' + window.location.search + ' #guesses-container');
		setTimeout(updateGuesses, 5000);
	}
}

/* Stolen from
 * https://stackoverflow.com/questions/19491336/get-url-parameter-jquery-or-how-to-get-query-string-values-in-js/21903119
 */
function getQueryParam(param) {
	"use strict";
	location.search.substr(1)
		.split("&")
		.some(function(item) { // returns first occurence and stops
			return item.split("=")[0] == param && (param = item.split("=")[1]);
		});
	return param;
}

$(function () {
	"use strict";
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
