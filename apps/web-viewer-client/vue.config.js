const HtmlWebpackPlugin = require('html-webpack-plugin');

// See available config at https://cli.vuejs.org/config/#vue-config-js
module.exports = {
  publicPath: '.',
  configureWebpack: {
    plugins: [
      new HtmlWebpackPlugin({
        title: 'Web viewer'
      })
    ]
  }
}

