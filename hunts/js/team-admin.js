import {BTable} from 'bootstrap-vue'
import URI from 'urijs'

import HumanDateTime from './human-datetime.vue'
import HumanDuration from './human-duration.vue'

export default {
  components: {
    'b-table': BTable,
    'human-datetime': HumanDateTime,
    'human-duration': HumanDuration,
  },
  computed: {
    sortedPuzzles() {
      function comparePuzzles(a, b) {
        const ad = new Date(a.guesses[0].given)
        const bd = new Date(b.guesses[0].given)
        return bd - ad
      }
      return [...this.puzzles].sort(comparePuzzles)
    },
  },
  created: function() {
    this.updateData(true)
  },
  data () {
    return {
      puzzles: [],
      solved_puzzles: [],
      'guess_fields': [
        'user',
        'guess',
        'given',
      ],
      'clue_fields': [
        'type',
        'text',
        'received_at',
      ],
    }
  },
  methods: {
    updateData: function(force) {
      clearTimeout(this.timer)
      if (force || this.autoUpdate) {
        let url = URI(this.href)
        let v = this
        fetch(url).then(
          response => response.json(),
        ).then(
          data => {
            v.puzzles = data.puzzles
            v.solved_puzzles = data.solved_puzzles
          },
        )
        if (this.autoUpdate) {
          this.timer = setTimeout(this.updateData, 5000)
        }
      }
    },
  },
  props: ['href'],
}
