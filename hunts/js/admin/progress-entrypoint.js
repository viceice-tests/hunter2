import Vue from 'vue'
import App from './progress.vue'
import 'bootstrap'
import { Slider } from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'

Vue.use(Slider)

const id = '#admin_progress_widget'
const el = document.querySelector(id)

new Vue({
  el: id,
  render: h => h(App, {
    props: {
      href: el.attributes.href.value,
    },
  }),
})
