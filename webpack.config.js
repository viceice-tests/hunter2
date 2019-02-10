const path = require('path');
const webpack = require('webpack');
const BundleTracker = require('webpack-bundle-tracker');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
  mode: 'production',
  context: '/usr/src/app',

  entry: {
    app: './app.js',
    hunter2: './hunter2/js/index.js',
    teams: './teams/js/index.js',
  },

  output: {
    path: path.resolve('assets/js/'),
    publicPath: 'http://localhost:4000/assets/js/',
    filename: '[name]/[hash].js',
    libraryTarget: 'var',
    library: '[name]'
  },

  devServer: {
    host: "0.0.0.0",
    port: 4000,
    hot: true
  },

  watch: true,
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
          'css-loader',
          'postcss-loader',
          'sass-loader'
        ]
      }
    ]
  },

  plugins: [
    new BundleTracker({filename: './webpack-stats.json'}), // Required for django-webpack-loader
    new MiniCssExtractPlugin({
      filename: '[name].css',
      chunkFilename: '[chunkhash].css'
    }),
    new webpack.HotModuleReplacementPlugin()
  ]
};
