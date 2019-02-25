import $ from 'jquery'
import 'bootstrap'

import '../scss/base.scss'

import setupJQueryAjaxCsrf from './csrf'

// TODO: Look at the best practice way of doing this.
$(function() {
  'use strict'
  setupJQueryAjaxCsrf()
})
