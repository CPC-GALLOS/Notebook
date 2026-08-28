/**
 * Custom Marp Engine for CPC Gallos Team Reference Document (TRD)
 * Automatically highlights competitive programming typedefs and aliases
 * (string, ll, ull, ld, pii, pll, uint, __int128, pt, Matrix, etc.) as standard C++ types.
 */

const { Marp } = require('@marp-team/marp-core')

module.exports = function marpCustomEngine(opts) {
  const marp = opts?.marp ?? new Marp(opts || {})
  const origHighlighter = marp.highlighter

  marp.highlighter = function customHighlighter(code, lang, ...args) {
    let res = origHighlighter ? origHighlighter.call(this, code, lang, ...args) : code

    if (lang === 'cpp' || lang === 'c++' || !lang) {
      const parts = res.split(/(<[^<>]*>)/)
      let inProtectedSpan = false

      for (let i = 0; i < parts.length; ++i) {
        const part = parts[i]
        if (part.startsWith('<span')) {
          if (
            part.includes('hljs-comment') ||
            part.includes('hljs-string') ||
            part.includes('hljs-meta') ||
            part.includes('hljs-doctag')
          ) {
            inProtectedSpan = true
          }
        } else if (part === '</span>') {
          inProtectedSpan = false
        } else if (!part.startsWith('<') && !inProtectedSpan) {
          parts[i] = part.replace(
            /\b(string|ll|ull|ld|pii|pll|uint|__int128|int128|pt|Matrix|ordered_set|gp_hash_table)\b/g,
            '<span class="hljs-type">$1</span>'
          )
        }
      }
      res = parts.join('')
    }
    return res
  }

  return marp
}
