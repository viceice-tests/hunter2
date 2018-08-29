$(document).ready(function() {
	"use strict";
	$('#inv-create').submit(function(event) {
		event.preventDefault();
		var field = $(this).find('select[name=user]');
		var user = field.val();
		var team = $(this).data('team');
		$.post(
			$(this).attr('action'), JSON.stringify({ user: user })
		).done(function(data) {
			$('#inv-error').text('').hide('fast');
			var cancel = $(`<a href="#" class="inv-cancel" data-user="${user}">Cancel</a>`);
			if (team) {
				cancel.data('team', team);
			}
			cancel.click(function() {
				cancel_invite($(this));
			});
			var list_entry = $(`<li style="display: none;">${data.username} has been invited<span style="float: right;">&nbsp;</span></li>`);
			list_entry.find('span').append(cancel);
			$('#inv-list').append(list_entry);
			list_entry.fadeIn('slow');
			field.empty();
		}).fail(function(jqXHR, textStatus, error) {
			var message = jqXHR.responseJSON.message;
			$('#inv-error').text(message).show('fast');
		});
	});

	function hide_invite(list_entry) {
		if (!list_entry.siblings().length) {
			$('#inv-div').hide('slow');
		}
		list_entry.fadeOut('slow', function() {
			$(this).remove();
		});
	}

	function cancel_invite(inv_button) {
		var prefix = inv_button.data('team') ? `${inv_button.data('team')}/` : '';
		var list_entry = inv_button.closest('li');
		$.post(
			prefix + 'cancelinvite', JSON.stringify({ user: inv_button.data('user') })
		).done(function() {
			$('#inv-error').text('').hide('fast');
			hide_invite(list_entry);
		}).fail(function(jqXHR, textStatus, error) {
			var message = jqXHR.responseJSON.message;
			if (jqXHR.responseJSON['delete']) {
				hide_invite(list_entry);
			}
			$('#inv-error').text(message).show('fast');
		});
	}
	$('.inv-cancel').click(function() {
		cancel_invite($(this));
	});

	$('.inv-accept').click(function() {
		var prefix = $(this).data('team') ? `${$(this).data('team')}/` : '';
		var list_entry = $(this).closest('li');
		$.post(
			prefix + 'acceptinvite'
		).done(function() {
			location.reload();
		}).fail(function(jqXHR, textStatus, error) {
			var message = jqXHR.responseJSON.message;
			if (jqXHR.responseJSON['delete']) {
				hide_invite(list_entry);
			}
			$('#inv-error').text(message).show('fast');
		});
	});

	$('.inv-deny').click(function() {
		var prefix = $(this).data('team') ? `${$(this).data('team')}/` : '';
		var list_entry = $(this).closest('li');
		$.post(
			prefix + 'denyinvite'
		).done(function() {
			$('#inv-error').text('').hide('fast');
			hide_invite(list_entry);
		}).fail(function(jqXHR, textStatus, error) {
			var message = jqXHR.responseJSON.message;
			if (jqXHR.responseJSON['delete']) {
				hide_invite(list_entry);
			}
			$('#inv-error').text(message).show('fast');
		});
	});

	$('#req-create').submit(function(event) {
		event.preventDefault();
		var field = $(this).find('select[name=team]');
		var team = field.val();
		$.post(
			team + '/request'
		).done(function(data) {
			$('#inv-error').text('').hide('fast');
			var cancel_link = $(`<a href="#" data-team="${team}">Cancel</a>`);
			cancel_link.click(function() {
				cancel_request($(this));
			});
			var list_entry = $(`<li style="display: none;">You have requested to join ${data.team}<span style="float: right;"></span></li>`);
			list_entry.find('span').append(cancel_link);
			$('#req-list').append(list_entry);
			list_entry.fadeIn('slow');
		}).fail(function(jqXHR, textStatus, error) {
			var message = jqXHR.responseJSON.message;
			if (jqXHR.responseJSON['delete']) {
				list_entry.fadeOut('slow', function() {
					$(this).remove();
				});
			}
			$('#req-error').text(message).show('fast');
		});
	});

	function hide_request(list_entry) {
		if (!list_entry.siblings().length) {
			$('#req-div').hide('slow');
		}
		list_entry.fadeOut('slow', function() {
			$(this).remove();
		});
	}
	
	function cancel_request(req_button) {
		var list_entry = req_button.closest('li');
		var list = req_button.closest('ul');
		$.post(
			req_button.data('team') + '/cancelrequest'
		).done(function() {
			$('#req-error').text('').hide('fast');
			hide_request(list_entry);
		}).fail(function(jqXHR, textStatus, error) {
			var message = jqXHR.responseJSON.message;
			if (jqXHR.responseJSON['delete']) {
				hide_request(list_entry);
			}
			$('#req-error').text(message).show('fast');
		});
	}
	$('.req-cancel').click(function() {
		cancel_request($(this)); }
	);

	$('.req-accept').click(function() {
		var prefix = $(this).data('team') ? `${$(this).data('team')}/` : '';
		var list_entry = $(this).closest('li');
		$.post(
			prefix + 'acceptrequest', JSON.stringify({ user: $(this).data('user') })
		).done(function(data) {
			$('#req-error').text('').hide('fast');
			hide_request(list_entry);
			var new_element = $(`<li>${data.username}<span style="float: right">&nbsp;${data.seat}</span></li>`);
			$('#member-list').append(new_element);
		}).fail(function(jqXHR, textStatus, error) {
			var message = jqXHR.responseJSON.message;
			if (jqXHR.responseJSON['delete']) {
				hide_request(list_entry);
			}
			$('#req-error').text(message).show('fast');
		});
	});

	$('.req-deny').click(function() {
		var prefix = $(this).data('team') ? `${$(this).data('team')}/` : '';
		var list_entry = $(this).closest('li');
		$.post(
			prefix + 'denyrequest', JSON.stringify({ user: $(this).data('user') })
		).done(function() {
			$('#req-error').text('').hide('fast');
			hide_request(list_entry);
		}).fail(function(jqXHR, textStatus, error) {
			var message = jqXHR.responseJSON.message;
			if (jqXHR.responseJSON['delete']) {
				hide_request(list_entry);
			}
			$('#req-error').text(message).show('fast');
		});
	});
});
