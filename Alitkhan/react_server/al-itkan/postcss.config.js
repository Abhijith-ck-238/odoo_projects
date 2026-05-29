const tailwindcss = require('tailwindcss');
module.exports = {
    plugins: [
        tailwindcss('./tailwind.js'),
        require('autoprefixer')
    ],
    theme: {
        colors: {
          indigo: '#5c6ac4',
          blue: '#007ace',
          red: '#de3618',
        }
      }
};
