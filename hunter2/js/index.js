import '../scss/base.scss';

import 'bootstrap';

// Expose global $ for jquery for now
require("expose-loader?$!jquery");

function getCookie(name) {
	"use strict";
	var cookieValue = null;
	if (document.cookie && document.cookie !== '') {
		var cookies = document.cookie.split(';');
		for (var i = 0; i < cookies.length; i++) {
			var cookie = $.trim(cookies[i]);
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) === (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}

function csrfSafeMethod(method) {
	"use strict";
	// these HTTP methods do not require CSRF protection
	return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function configureCSRF() {
	"use strict";
	var csrftoken = getCookie('csrftoken');
	$.ajaxSetup({
		beforeSend: function(xhr, settings) {
			if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
				xhr.setRequestHeader('X-CSRFToken', csrftoken);
			}
		},
		contentType: 'application/json'
	});
}

// TODO: Look at the best practice way of doing this.
configureCSRF();
