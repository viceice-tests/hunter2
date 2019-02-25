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
    'rules': {
        'indent': [
            'error',
            2,
        ],
        'linebreak-style': [
            'error',
            'unix',
        ],
        'overrides': [
            {
                'env': {
                    'commonjs': true,
                },
                'files': [
                    'webpack.*.js',
                ],
            },
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
