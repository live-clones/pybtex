const purgecss = require('@fullhuman/postcss-purgecss')({

  // Specify the paths to all of the template files in your project 
  content: [
    '../build/**/*.html',
    // etc.
  ],
  whitelist: ['highlighted'],

  // Include any special characters you're using in this regular expression
  // defaultExtractor: content => content.match(/[\w-/:]+(?<!:)/g) || []
})

module.exports = {
  plugins: [
    require('tailwindcss'),
    require('autoprefixer'),
    purgecss,
    require('cssnano')({
      preset: 'default',
    }),
  ]
}
