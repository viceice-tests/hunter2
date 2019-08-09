import $ from 'jquery'

import setupJQueryAjaxCsrf from './csrf'

// Fuck JS and its lack of a standard library
var entityMap = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  '\'': '&#39;',
  '/': '&#x2F;',
  '`': '&#x60;',
  '=': '&#x3D;',
  ' ': '&nbsp;',
}

export function escapeHtml (string) {
  return String(string).replace(/[&<>"'`=/ ]/g, function (s) {
    return entityMap[s]
  })
}

$(function() {
  setupJQueryAjaxCsrf()
  $('#logoutLink').click(function() {
    $('#logoutForm').submit()
  })
})
