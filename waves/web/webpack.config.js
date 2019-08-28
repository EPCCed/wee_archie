module.exports = {
    entry: './src/index.js',
    output: {
        path: __dirname + '/lib',
        filename: 'index.js',
        library: '@wee-archie/wave-demo',
        libraryTarget: 'umd',
    },
    module: {
        rules: [
            {
                test: /\.(js|jsx)$/i,
                exclude: /node_modules/,
                use: ['babel-loader'],
            },
            {
                test: /\.css$/i,
                // style-loader
                use: [
                    { loader: 'style-loader' },
                    // css-loader
                    {
                        loader: 'css-loader',
                        options: {
                            modules: {
                                localIdentName: "[name]__[local]___[hash:base64:5]",
                            }
                        }
                    },
                    {
                        loader: 'postcss-loader',
                        options: { ident: 'postcss' }
                    }
                ]
            },
            {
                test: /\.(png|svg|jpe?g|gif)$/i,
                use: [
                    'url-loader',
                    {
                        loader: 'image-webpack-loader',
                        options: {
                            mozjpeg: {
                              progressive: true,
                              quality: 65
                            },
                            pngquant: {
                              quality: '65-90',
                              speed: 4
                            },
                        }
                    }
                ]
            }
        ],
    },
    externals : {
        react: 'react'
    },
};
