import $ from 'jquery'
import 'bootstrap'
import Vue from 'vue'

import 'hunter2/js/base'
import AdminGuessList from './admin-guess-list.vue'

$(function () {
  const href = $('#admin-guess-list').data('href')
  const adminguesslist = new Vue({
    ...AdminGuessList,
    propsData: {
      href: href,
    },
  })
  adminguesslist.$mount('#admin-guess-list')
})
