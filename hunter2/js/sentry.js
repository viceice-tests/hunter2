import Vue from 'vue'
import * as Sentry from '@sentry/browser'
import * as Integrations from '@sentry/integrations'

if (window.sentry_dsn) {
  Sentry.init({
    dsn: window.sentry_dsn,
    integrations: [
      new Integrations.Vue({Vue, attachProps: true}),
    ],
  })
}
