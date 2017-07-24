function updateGuesses(ignore) {
	if (ignore || $('#auto-update').prop('checked')) {
		$('#guesses-container').load('guesses_content #guesses-table');
		setTimeout(updateGuesses, 5000);
	}
}

function updateClicked(ev) {
	if ($(this).prop('checked')) {
		updateGuesses();
	}
}

$(function () {
	updateGuesses(true);
	$('#auto-update').click(updateClicked);
});
