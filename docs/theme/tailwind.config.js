module.exports = {
  theme: {
    fontFamily: {
      sans: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Helvetica Neue', 'Noto Sans', 'Roboto', 'Verdana', 'sans-serif', 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji'],
      serif: ['Noto Serif', 'Georgia', 'Cambria', 'Times New Roman', 'Times', 'serif'],
      mono: ['Menlo', 'Monaco', 'Noto Sans Mono', 'Source Code Pro', 'Consolas', 'Courier New', 'Liberation Mono', 'monospace']
    },
    listStyleType: {
      none: 'none',
      disc: 'disc',
      decimal: 'decimal',
      circle: 'circle'
    },
  },
  purge: ['../build/**/*.html'],
  future: {
    purgeLayersByDefault: true,
    removeDeprecatedGapUtilities: true,
  },
}
