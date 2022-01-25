const fs = require('fs')
const tex2svg = require('./tex2svg.js')

let { argv } = process
tex2svg(argv[3]).then(svg => fs.writeFileSync(argv[2], svg))
