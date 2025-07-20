const path = require('path');
const { defineConfig } = require('vite')

module.exports = defineConfig({
    build: {
        outDir: path.resolve(__dirname, '../../static/js'),
        minify: true,
        rollupOptions: {
            output: {
                entryFileNames: '[name].js',
                format: 'es',
                inlineDynamicImports: false
              },
            input: {
                'registros': './index-registros.js',
                'generic-registros': './generic-registros.js'
            },
        }
    }
});
