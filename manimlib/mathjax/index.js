const fs = require('fs')
const tex2svg = require('./tex2svg.js')

let { argv } = process
if (argv[2] === '-v') {
    console.log(process.argv)
    argv = argv.slice(1)
}
tex2svg(argv[3]).then(svg => fs.writeFileSync(argv[2], svg))
