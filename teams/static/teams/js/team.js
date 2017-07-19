$(document).ready(function() {
	$('#inv-create').submit(function(event) {
		event.preventDefault();
		var $user = $(this).children('select[name=user]').val();
		$.post(
			$(this).attr('action'), JSON.stringify({ user: $user })
		).done(function(data) {
			var $cancel_button = $(`<button type="button" class="btn btn-danger inv-cancel" autocomplete="off" value="${$user}">Cancel</button>`);
			$cancel_button.click(cancel_invite);
			var $new_element = $(`<li>${data.username}\n</li>`).append($cancel_button);
			$('#inv-list').append($new_element);
		});
	});

	function cancel_invite() {
		var $list_entry = $(this).parent('li');
		$.post(
			'cancelinvite', JSON.stringify({ user: $(this).attr('value') })
		).done(function() {
			$list_entry.remove();
		});
	}
	$('.inv-cancel').click(cancel_invite);

	$('.inv-accept').click(function() {
		$.post(
			'acceptinvite'
		).done(function() {
			location.reload();
		});
	});

	$('.inv-deny').click(function() {
		var $invite_section = $(this).closest('div');
		$.post(
			'denyinvite'
		).done(function() {
			$invite_section.remove();
		});
	});

	function create_request() {
		var $request_section = $(this).closest('div');
		$.post(
			'request'
		).done(function() {
			$cancel_button = $(`<button type="button" class="btn btn-danger req-cancel" autocomplete="off">Cancel</button>`);
			$cancel_button.click(cancel_request);
			$request_section.replaceWith(`
<div id="req-div">
	<h2>Request</h2>
	<p>
		You have requested to join this team.
	</p>
</div>
			`);
			$('#req-div p').append($cancel_button);
		});
	}
	$('.req-create').click(create_request);

	function cancel_request() {
		var $request_section = $(this).closest('div');
		$.post(
			'cancelrequest'
		).done(function() {
			$create_button= $(`<button type="button" class="btn btn-primary req-create" autocomplete="off">Request</button>`);
			$create_button.click(create_request);
			$request_section.replaceWith(`
<div id="req-div">
	<h2>Request</h2>
	<p>
		Request to join this team:
	</p>
</div>
			`);
			$('#req-div p').append($create_button);
		});
	}
	$('.req-cancel').click(cancel_request);

	$('.req-accept').click(function() {
		var $list_entry = $(this).parent('li');
		$.post(
			'acceptrequest', JSON.stringify({ user: $(this).attr('value') })
		).done(function(data) {
			$list_entry.remove();
			var $new_element = $(`<li>${data.username}\n</li>`);
			$('#member-list').append($new_element);
		});
	});

	$('.req-deny').click(function() {
		var $list_entry = $(this).parent('li');
		$.post(
			'denyrequest', JSON.stringify({ user: $(this).attr('value') })
		).done(function() {
			$list_entry.remove();
		});
	});
})
