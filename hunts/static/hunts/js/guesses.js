function updateGuesses(force) {
	if (force || $('#auto-update').prop('checked')) {
		$('#fill-me-up-you-slut').load('guesses_content' + window.location.search + ' #guesses-container');
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
