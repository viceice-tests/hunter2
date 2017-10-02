function updateGuesses(force) {
	"use strict";
	if (force || $('#auto-update').prop('checked')) {
		$('#fill-me-up-you-slut').load('guesses_content' + window.location.search + ' #guesses-container');
		setTimeout(updateGuesses, 5000);
	}
}

$(function () {
	"use strict";
	updateGuesses(true);
	$('#auto-update').click(function (ev) {
		if ($(this).prop('checked')) {
			updateGuesses();
		}
	});
});
