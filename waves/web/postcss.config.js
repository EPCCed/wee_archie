module.exports = {
  "plugins": [
    require('autoprefixer')
],
  "postcss": {
    "parser": "sugarss",
    "map": false,
    "plugins": {
      "autoprefixer": {},
    }
  }
}
