const path = require('path');
const webpack = require('webpack');
const BundleTracker = require('webpack-bundle-tracker');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
  context: '/usr/src/app',

  entry: {
    hunter2: './hunter2/js/index.js',
    teams: './teams/js/index.js',
  },

  output: {
    path: path.resolve('assets/bundles/'),
    filename: '[name]/[hash].js',
    libraryTarget: 'var',
    library: '[name]'
  },

  module: {
    rules: [
      {
        test: /\.(scss)$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader?sourceMap',
          'postcss-loader?sourceMap',
          'sass-loader?sourceMap'
        ]
      }
    ]
  },

  plugins: [
    new BundleTracker({filename: './webpack-stats.json'}), // Required for django-webpack-loader
    new MiniCssExtractPlugin({
      filename: '[name]/[hash].css',
    }),
  ]
};
