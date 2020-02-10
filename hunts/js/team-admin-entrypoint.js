import Vue from 'vue'
import App from './team-admin.vue'
import vueMoment from 'vue-moment'

Vue.use(vueMoment)

const id = '#team_puzzles_admin_widget'
const el = document.querySelector(id)

new Vue({
  el: id,
  render: h => h(App, {
    props: {
      href: el.attributes.href.value,
    },
  }),
})
