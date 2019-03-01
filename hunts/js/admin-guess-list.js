import $ from 'jquery'
import URI from 'urijs'

export default {
  created: function() {
    this.updateData(true)
  },
  data: function() {
    return {
      autoUpdate: true,
      guesses: [],
      pages: {
        current: 0,
        total: 0,
        next: '',
        previous: '',
      },
    }
  },
  methods: {
    updateData: function(force) {
      let v = this
      if (force || this.autoUpdate) {
        $.get(this.href).done(function(data) {
          v.guesses = data.guesses
          v.pages.current = data.pages.current
          v.pages.total = data.pages.total
          let url = URI(window.location)
          v.pages.next = data.pages.next ? url.addSearch({page: data.pages.next}) : ''
          v.pages.previous = data.pages.previous ? url.addSearch({page: data.pages.previous}) : ''
        })
        setTimeout(this.updateData, 5000)
      }
    },
  },
  props: [
    'href',
  ],
  watch: {
    autoUpdate: function(on) {
      if (on) {
        this.updateData()
      }
    },
  },
}
