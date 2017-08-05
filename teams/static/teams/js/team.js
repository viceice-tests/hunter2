$(document).ready(function() {
	$('#inv-create').submit(function(event) {
		event.preventDefault();
		var $field = $(this).find('select[name=user]');
		var $user = $field.val();
		var $team = $(this).data('team');
		$.post(
			$(this).attr('action'), JSON.stringify({ user: $user })
		).done(function(data) {
			var $cancel = $(`<a href="#" class="inv-cancel" data-user="${$user}">Cancel</a>`);
			if ($team) {
				$cancel.data('team', $team);
			}
			$cancel.click(cancel_invite);
			var $new_element = $(`<li>${data.username}<span style="float: right">&nbsp;</span></li>`);
			$new_element.find('span').append($cancel);
			$('#inv-list').append($new_element);
			$field.empty();
		});
	});

	function cancel_invite() {
		var $prefix = $(this).data('team') ? `${$(this).data('team')}/` : ''
		var $list_entry = $(this).closest('li');
		$.post(
			$prefix + 'cancelinvite', JSON.stringify({ user: $(this).data('user') })
		).done(function() {
			$list_entry.fadeOut(300, function() {
				$(this).fadeOut(300, function() {
					$(this).remove();
				});
			});
		});
	}
	$('.inv-cancel').click(cancel_invite);

	$('.inv-accept').click(function() {
		var $prefix = $(this).data('team') ? `${$(this).data('team')}/` : ''
		$.post(
			$prefix + 'acceptinvite'
		).done(function() {
			location.reload();
		});
	});

	$('.inv-deny').click(function() {
		var $prefix = $(this).data('team') ? `${$(this).data('team')}/` : ''
		var $invite_section = $(this).closest('li');
		$.post(
			$prefix + 'denyinvite'
		).done(function() {
			$invite_section.fadeOut(300, function() {
				$(this).remove();
			});
		});
	});

	function create_request() {
		var $request_section = $(this).closest('div');
		$.post(
			'request'
		).done(function() {
			var $cancel_button = $(`<button type="button" class="btn btn-danger req-cancel" autocomplete="off">Cancel</button>`);
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
			$list_entry.fadeOut(300, function() {
				$(this).remove();
			});
			var $new_element = $(`<li>${data.username}\n</li>`);
			$('#member-list').append($new_element);
		});
	});

	$('.req-deny').click(function() {
		var $list_entry = $(this).parent('li');
		$.post(
			'denyrequest', JSON.stringify({ user: $(this).attr('value') })
		).done(function() {
			$list_entry.fadeOut(300, function() {
				$(this).remove();
			});
		});
	});
})
