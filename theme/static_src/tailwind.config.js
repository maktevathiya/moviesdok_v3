module.exports = {
    content: [
        //'../templates/**/*.html',
        //'../../templates/**/*.html',
        //'../../**/templates/**/*.html',

        '../../templates/**/*.html',
        './node_modules/flowbite/**/*.js',
    ],
    theme: {
        extend: {
          fontFamily: {
            roboto: ['Roboto', 'Arial', 'sans-serif'], // Use Roboto font family
          },
          backdropBlur: {
            '0.5': '0.5px', 
            '1': '1px',        
          },
          lineClamp: {
            8: '8',  // Add line-clamp-8
          },
        },
    },
    plugins: [
        
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
        require('@tailwindcss/line-clamp'),

    ],
}
