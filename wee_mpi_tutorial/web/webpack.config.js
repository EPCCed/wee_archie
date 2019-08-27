module.exports = {
    entry: './src/index.js',
    output: {
        path: __dirname + '/lib',
        filename: 'index.js',
        library: '@wee-archie/wee-mpi-tutorial',
        libraryTarget: 'umd',
    },
    module: {
        rules: [
            {
                test: /\.(js|jsx)$/i,
                exclude: /node_modules/,
                use: ['babel-loader'],
            },
        ],
    },
    externals : {
        react: 'react'
    },
};
