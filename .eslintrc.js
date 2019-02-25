module.exports = {
    'env': {
        'browser': true,
        'es6': true,
    },
    'extends': 'eslint:recommended',
    'globals': {
        'Atomics': 'readonly',
        'SharedArrayBuffer': 'readonly',
    },
    'parserOptions': {
        'ecmaVersion': 2018,
        'sourceType': 'module',
    },
    'overrides': [
        {
            'env': {
                'node': true,
            },
            'files': [
                'postcss.config.js',
                'webpack.*.js',
            ],
        },
    ],
    'rules': {
        'indent': [
            'error',
            2,
        ],
        'linebreak-style': [
            'error',
            'unix',
        ],
        'quotes': [
            'error',
            'single',
        ],
        'semi': [
            'error',
            'never',
        ],
        'strict': [
            'error',
        ],
    }
}
