import $ from 'jquery'

import setupJQueryAjaxCsrf from './csrf'

$(function() {
  setupJQueryAjaxCsrf()
  $('#logoutLink').click(function() {
    $('#logoutForm').submit()
  })
})
