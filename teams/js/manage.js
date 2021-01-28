// The forms on this page use Django widgets which expect jquery
// to be loaded into the global scope as $ and jQuery
import $ from 'expose-loader?exposes[]=$&exposes[]=jQuery!jquery'

import 'hunter2/js/base.js'
import 'hunter2/js/csrf.js'
import * as invite from './invite.js'
import * as request from './request.js'

import '../scss/team_members.scss'

$(function(){
  $('#inv-create').on('submit', invite.create)
  $('.inv-accept').on('click', invite.accept)
  $('.inv-deny').on('click', invite.decline)
  $('.inv-cancel').on('click', invite.cancel)

  $('#req-create').on('submit', request.create)
  $('.req-accept').on('click', request.accept)
  $('.req-deny').on('click', request.decline)
  $('.req-cancel').on('click', request.cancel)
})
