const path = require('path');
const webpack = require('webpack');
const BundleTracker = require('webpack-bundle-tracker');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
  devtool: 'source-map',
  mode: 'development',
  context: '/usr/src/app',

  entry: {
    hunter2: './hunter2/js/index.js',
    teams: './teams/js/index.js',
  },

  output: {
    path: path.resolve('./assets/bundles/'),
    publicPath: 'http://localhost:4000/assets/bundles/',
    filename: '[name]/[hash].js',
    libraryTarget: 'var',
    library: '[name]'
  },

  devServer: {
    host: "0.0.0.0",
    port: 4000,
  },

  watch: false,
  watchOptions: {
    aggregateTimeout: 300,
    poll: 1000,
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
