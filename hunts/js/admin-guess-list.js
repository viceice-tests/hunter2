import $ from 'jquery'
import BPagination from 'bootstrap-vue/es/components/pagination/pagination'
import URI from 'urijs'

export default {
  components: {
    'b-pagination': BPagination,
  },
  created: function() {
    this.updateData(true)
  },
  data: function() {
    return {
      autoUpdate: true,
      currentPage: 1,
      guesses: [],
      pages: {
        current: 0,
        total: 0,
        next: '',
        previous: '',
      },
      perPage: 50,
      rows: 0,
    }
  },
  methods: {
    changePage: function(page) {
      this.autoUpdate = page === 1
      this.updateData(true, page)
    },
    updateData: function(force, page) {
      if (page === undefined) {
        page = this.currentPage
      }
      if (force || this.autoUpdate) {
        let guesses_url = URI(this.href).query({'page': page})
        let v = this
        $.get(guesses_url).done(function(data) {
          v.guesses = data.guesses
          v.rows = data.rows
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
