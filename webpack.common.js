const path = require('path')
const BundleTracker = require('webpack-bundle-tracker')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')

module.exports = {
  context: '/usr/src/app',

  entry: {
    hunter2:       './hunter2/js/index.js',
    teams_manage:  './teams/js/manage.js',
    hunts_event:   './hunts/js/event.js',
    hunts_puzzle:  './hunts/js/puzzle.js',
    hunts_stats:   './hunts/js/stats.js',
    hunts_guesses: './hunts/js/guesses.js',
  },

  module: {
    rules: [
      {
        test: /\.(scss)$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader?sourceMap',
          'postcss-loader?sourceMap',
          'sass-loader?sourceMap',
        ],
      },
    ],
  },

  output: {
    path: path.resolve('assets/bundles/'),
    filename: '[name]/[hash].js',
    libraryTarget: 'var',
    library: '[name]',
  },

  plugins: [
    new BundleTracker({filename: './webpack-stats.json'}), // Required for django-webpack-loader
    new MiniCssExtractPlugin({
      filename: '[name]/[hash].css',
    }),
  ],

  resolve: {
    modules: [
      path.resolve('.'),
      path.resolve('./node_modules'),
    ],
  },
}
