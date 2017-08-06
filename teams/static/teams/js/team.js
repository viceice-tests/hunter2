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
			var $list_entry = $(`<li hidden>${data.username} has been invited<span style="float: right">&nbsp;</span></li>`);
			$list_entry.find('span').append($cancel);
			$('#inv-list').append($list_entry);
			$list_entry.fadeIn('slow');
			$field.empty();
		});
	});

	function cancel_invite() {
		var $prefix = $(this).data('team') ? `${$(this).data('team')}/` : ''
		var $list_entry = $(this).closest('li');
		$.post(
			$prefix + 'cancelinvite', JSON.stringify({ user: $(this).data('user') })
		).done(function() {
			if (!$list_entry.siblings().length) {
				$('#inv-div').hide('slow');
			}
			$list_entry.fadeOut('slow', function() {
				$(this).remove();
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
		var $list_entry = $(this).closest('li');
		$.post(
			$prefix + 'denyinvite'
		).done(function() {
			if ($list_entry.siblings().length == 0) {
				$('#inv-div').hide('slow')
			}
			$list_entry.fadeOut('slow', function() {
				$(this).remove();
			});
		});
	});

	$('#req-create').submit(function(event) {
		event.preventDefault();
		var $field = $(this).find('select[name=team]');
		var $team = $field.val();
		$.post(
			$team + '/request'
		).done(function(data) {
			var $cancel_link = $(`<a href="#" data-team="${$team}">Cancel</a>`);
			$cancel_link.click(cancel_request);
			var $list_entry = $(`<li hidden>You have requested to join ${data['team']}<span style="float: right"></span></li>`);
			$list_entry.find('span').append($cancel_link);
			$('#req-list').append($list_entry);
			$list_entry.fadeIn('slow');
		});
	});
	
	function cancel_request() {
		var $list_entry = $(this).closest('li');
		var $list = $(this).closest('ul');
		$.post(
			$(this).data('team') + '/cancelrequest'
		).done(function() {
			$list_entry.fadeOut('slow', function() {
				$(this).remove();
			});
		});
	}
	$('.req-cancel').click(cancel_request);

	$('.req-accept').click(function() {
		var $prefix = $(this).data('team') ? `${$(this).data('team')}/` : ''
		var $list_entry = $(this).closest('li');
		$.post(
			$prefix + 'acceptrequest', JSON.stringify({ user: $(this).data('user') })
		).done(function(data) {
			if ($list_entry.siblings().length == 0) {
				$('#req-div').hide('slow');
			}
			$list_entry.fadeOut('slow', function() {
				$(this).remove();
			});
			var $new_element = $(`<li>${data.username}<span style="float: right">&nbsp;${data.seat}</span></li>`);
			$('#member-list').append($new_element);
		});
	});

	$('.req-deny').click(function() {
		var $prefix = $(this).data('team') ? `${$(this).data('team')}/` : ''
		var $list_entry = $(this).closest('li');
		$.post(
			$prefix + 'denyrequest', JSON.stringify({ user: $(this).data('user') })
		).done(function() {
			if ($list_entry.siblings().length == 0) {
				$('#req-div').hide('slow');
			}
			$list_entry.fadeOut('slow', function() {
				$(this).remove();
			});
		});
	});
})
