import $ from 'jquery'
import 'bootstrap'
import URI from 'urijs'
import Vue from 'vue'

import '../scss/guesses.scss'

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

  const autoUpdate = $('#auto-update')
  const page = parseInt(URI(location).search(true)['page'])
  if (page > 1) {
    autoUpdate.prop('checked', false)
  }

  const guessesData = {
    guesses: [],
    pages: {
      current: 0,
      next: 0,
      previous: 0,
      total: 0,
    },
    update: function() {
      if (autoUpdate.prop('checked')) {
        setTimeout(this.update, 5000)
      }
    },
  }

  autoUpdate.click(function () {
    if ($(this).prop('checked')) {
      guessesData.update()
    }
  })

  guessesData.update()
})
