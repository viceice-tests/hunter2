import $ from 'jquery'

function hide(list_entry) {
  if (!list_entry.siblings().length) {
    $('#req-div').hide('slow')
  }
  list_entry.fadeOut('slow', function() {
    $(this).remove()
  })
}

export function cancel(event) {
  var target = $(event.target)
  var list_entry = target.closest('li')
  $.post(
    target.data('team') + '/cancelrequest',
  ).done(function() {
    $('#req-error').text('').hide('fast')
    hide(list_entry)
  }).fail(function(jqXHR) {
    var message = jqXHR.responseJSON.message
    if (jqXHR.responseJSON['delete']) {
      hide(list_entry)
    }
    $('#req-error').text(message).show('fast')
  })
}

export function create(event) {
  event.preventDefault()
  var target = $(event.target)
  var field = target.find('select[name=team]')
  var team = field.val()
  $.post(
    team + '/request',
  ).done(function(data) {
    $('#inv-error').text('').hide('fast')
    var cancel_link = $(`<a href="#" data-team="${team}">Cancel</a>`)
    cancel_link.on('click', cancel)
    var list_entry = $(`<li style="display: none;">You have requested to join ${data.team}<span style="float: right;"></span></li>`)
    list_entry.find('span').append(cancel_link)
    $('#req-list').append(list_entry)
    list_entry.fadeIn('slow')
  }).fail(function(jqXHR) {
    var message = jqXHR.responseJSON.message
    $('#req-error').text(message).show('fast')
  })
}

export function accept(event) {
  var target = $(event.target)
  var prefix = target.data('team') ? `${target.data('team')}/` : ''
  var list_entry = target.closest('li')
  $.post(
    prefix + 'acceptrequest', JSON.stringify({ user: target.data('user') }),
  ).done(function(data) {
    $('#req-error').text('').hide('fast')
    hide(list_entry)
    var new_element = `<div class="member"><h3><a href="${data.url}">${data.username}</a></h3>`
    if (data.picture) { new_element += `<img src="${data.picture}" alt="${data.username}" />` }
    new_element += '<p>'
    if (data.seat) { new_element += `Seat ${data.seat}` }
    new_element += '</p></div>'
    $('#member-list').append($(new_element))
  }).fail(function(jqXHR) {
    var message = jqXHR.responseJSON.message
    if (jqXHR.responseJSON['delete']) {
      hide(list_entry)
    }
    $('#req-error').text(message).show('fast')
  })
}

export function decline(event) {
  var target = $(event.target)
  var prefix = target.data('team') ? `${target.data('team')}/` : ''
  var list_entry = target.closest('li')
  $.post(
    prefix + 'denyrequest', JSON.stringify({ user: target.data('user') }),
  ).done(function() {
    $('#req-error').text('').hide('fast')
    hide(list_entry)
  }).fail(function(jqXHR) {
    var message = jqXHR.responseJSON.message
    if (jqXHR.responseJSON['delete']) {
      hide(list_entry)
    }
    $('#req-error').text(message).show('fast')
  })
}
