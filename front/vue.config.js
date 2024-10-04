const { defineConfig } = require('@vue/cli-service');

module.exports = defineConfig({
  devServer: {
    proxy: {
      '/auth/': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        ws: false,
      }
    }
  },
  outputDir: '../static/frontend',
  publicPath: process.env.NODE_ENV === 'production' ? '/static/frontend/' : '/',
  filenameHashing: false,
  css: {
    extract: true,
  },
  transpileDependencies: true,
});

module.exports = {
  chainWebpack: config => {
    config.plugin('define').tap((definitions) => {
      Object.assign(definitions[0]['process.env'], {
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: JSON.stringify(true),
      });
      return definitions;
    });
  },
};
