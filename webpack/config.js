var path = require('path');
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');

module.exports = {
	context: __dirname,

	entry: {
		hunter2: '../hunter2/js/index.js',
	},

	mode: 'production',

	output: {
		path: path.resolve('../assets/js/'),
		filename: "[name]/[hash].js",
		libraryTarget: 'var',
		library: '[name]'
	},

	plugins: [
		new BundleTracker({filename: './webpack-stats.json'}),
		new webpack.ProvidePlugin({'Raven': 'raven-js'})
	]
};
