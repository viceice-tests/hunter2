import $ from 'jquery'

function toggleAdvanced(event, display, duration) {
  if (event !== undefined) {
    event.preventDefault()
  }

  let fields = $('.advanced_field').map(function() {
    return this.closest('div.form-row')
  })

  if (display == undefined) {
    display = !fields.is(':visible')
  }

  if (duration == undefined) {
    duration = 'slow'
  }

  let button_verb
  if (display) {
    button_verb = 'Hide'
    fields.show(duration)
  } else {
    button_verb = 'Show'
    fields.hide(duration)
  }

  $('#advanced_button').html(`${button_verb} Advanced Options`)
}

$(function() {
  toggleAdvanced(undefined, false, 0)
  $('#advanced_button').click(toggleAdvanced)
})
