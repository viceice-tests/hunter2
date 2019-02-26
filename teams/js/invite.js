import $ from 'jquery';

function hide(list_entry) {
	"use strict";
	if (!list_entry.siblings().length) {
		$('#inv-div').hide('slow');
	}
	list_entry.fadeOut('slow', function() {
		$(this).remove();
	});
}

export function cancel(event) {
	"use strict";
	var target = $(event.target);
	var prefix = target.data('team') ? `${target.data('team')}/` : '';
	var list_entry = target.closest('li');
	$.post(
		prefix + 'cancelinvite', JSON.stringify({ user: target.data('user') })
	).done(function() {
		$('#inv-error').text('').hide('fast');
		hide(list_entry);
	}).fail(function(jqXHR, textStatus, error) {
		var message = jqXHR.responseJSON.message;
		if (jqXHR.responseJSON['delete']) {
			hide(list_entry);
		}
		$('#inv-error').text(message).show('fast');
	});
}

export function create(event) {
	"use strict";
	event.preventDefault();
	var target = $(event.target);
	var field = target.find('select[name=user]');
	var user = field.val();
	var team = target.data('team');
	$.post(
		target.attr('action'), JSON.stringify({ user: user })
	).done(function(data) {
		$('#inv-error').text('').hide('fast');
		var cancel_link = $(`<a href="#" class="inv-cancel" data-user="${user}">Cancel</a>`);
		cancel_link.on('click', cancel);
		if (team) {
			cancel_link.data('team', team);
		}
		var list_entry = $(`<li style="display: none;">${data.username} has been invited<span style="float: right;">&nbsp;</span></li>`);
		list_entry.find('span').append(cancel_link);
		$('#inv-list').append(list_entry);
		list_entry.fadeIn('slow');
		field.empty();
	}).fail(function(jqXHR, textStatus, error) {
		var message = jqXHR.responseJSON.message;
		$('#inv-error').text(message).show('fast');
	});
}

export function accept(event) {
	"use strict";
	var target = $(event.target);
	var prefix = target.data('team') ? `${target.data('team')}/` : '';
	var list_entry = target.closest('li');
	$.post(
		prefix + 'acceptinvite'
	).done(function() {
		location.reload();
	}).fail(function(jqXHR, textStatus, error) {
		var message = jqXHR.responseJSON.message;
		if (jqXHR.responseJSON['delete']) {
			hide(list_entry);
		}
		$('#inv-error').text(message).show('fast');
	});
}

export function decline(event) {
	"use strict";
	var target = $(event.target);
	var prefix = target.data('team') ? `${target.data('team')}/` : '';
	var list_entry = target.closest('li');
	$.post(
		prefix + 'denyinvite'
	).done(function() {
		$('#inv-error').text('').hide('fast');
		hide(list_entry);
	}).fail(function(jqXHR, textStatus, error) {
		var message = jqXHR.responseJSON.message;
		if (jqXHR.responseJSON['delete']) {
			hide(list_entry);
		}
		$('#inv-error').text(message).show('fast');
	});
}
