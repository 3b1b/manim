//const fs = require('fs')

// Cannot use let/const here
MathJax = {
  loader: {
    paths: {mathjax: 'mathjax-full/es5'},
    require: require,
    load: ['adaptors/liteDOM']
  },
  tex: {
    packages: ['base', 'autoload', 'require', 'ams', 'newcommand'],
  },
  svg: {
    fontCache: 'local'
  },
  startup: {
    typeset: false
  }
}

//  Load the MathJax startup module
require('mathjax-full/es5/tex-svg.js')

const texConfig = {
  display: true, // `false` for inline formulas
  em: 32,
  ex: 16,
  containerWidth: 80 * 16,
}

async function tex2svg (tex, debug) {
  await MathJax.startup.promise
  const dirtySvg = await MathJax.tex2svgPromise(tex, texConfig).then(node =>
    MathJax.startup.adaptor.innerHTML(node)
  )
  const lastIndex = dirtySvg.lastIndexOf('</svg>')
  const svg = dirtySvg.slice(0, lastIndex + 6) // '</svg>'.length === 6

  // Plan A, failed
  //const res = svgo.optimize(svg, svgoConfig)
  //if (!res.data) throw res

  // Plan B, failed
  //return flatten(svg).transform().value().toString()

  // Plan C, failed
  //return pathologist.transform(svg)

  //if (debug)
  //  fs.writeFileSync(debug, svg)
  return svg
}

module.exports = tex2svg
