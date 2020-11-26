import {format, formatDistanceToNow, isFuture} from 'date-fns'

export default {
  filters: {
    formatLocale: function(value) {
      return format(new Date(value), 'PPPPpppp')
    },
    formatDistanceToNow: function(value) {
      const date = new Date(value)
      const [prefix, suffix] = isFuture(date) ? ['in ', ''] : ['', ' ago']
      return `${prefix}${formatDistanceToNow(date)}${suffix}`
    },
  },
  props: ['value', 'title'],
}
