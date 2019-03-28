import $ from 'jquery'
import 'bootstrap'
import Vue from 'vue'

import AdminGuessList from './admin-guess-list.vue'
import setupJQueryAjaxCsrf from 'hunter2/js/csrf.js'

$(function () {
  setupJQueryAjaxCsrf()

  Vue.component('admin-guess-list', AdminGuessList)

  new Vue({
    components: {
      'admin-guess-list': AdminGuessList,
    },
    el: '#content',
  })
})
