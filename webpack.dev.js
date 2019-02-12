const merge = require('webpack-merge');
const common = require('./webpack.common.js');

module.exports = merge(common, {
  mode: 'development',
  devtool: 'source-map',

  output: {
    publicPath: 'http://localhost:4000/assets/bundles/',
  },

  devServer: {
    host: "0.0.0.0",
    port: 4000,
    disableHostCheck: true
  },

  watchOptions: {
    aggregateTimeout: 300,
    poll: 1000,
  },
});
