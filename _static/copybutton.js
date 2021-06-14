// Localization support
const messages = {
  'en': {
    'copy': 'Copy',
    'copy_to_clipboard': 'Copy to clipboard',
    'copy_success': 'Copied!',
    'copy_failure': 'Failed to copy',
  },
  'es' : {
    'copy': 'Copiar',
    'copy_to_clipboard': 'Copiar al portapapeles',
    'copy_success': '¡Copiado!',
    'copy_failure': 'Error al copiar',
  },
  'de' : {
    'copy': 'Kopieren',
    'copy_to_clipboard': 'In die Zwischenablage kopieren',
    'copy_success': 'Kopiert!',
    'copy_failure': 'Fehler beim Kopieren',
  },
  'fr' : {
    'copy': 'Copier',
    'copy_to_clipboard': 'Copié dans le presse-papier',
    'copy_success': 'Copié !',
    'copy_failure': 'Échec de la copie',
  },
  'ru': {
    'copy': 'Скопировать',
    'copy_to_clipboard': 'Скопировать в буфер',
    'copy_success': 'Скопировано!',
    'copy_failure': 'Не удалось скопировать',
  },
  'zh-CN': {
    'copy': '复制',
    'copy_to_clipboard': '复制到剪贴板',
    'copy_success': '复制成功!',
    'copy_failure': '复制失败',
  }
}

let locale = 'en'
if( document.documentElement.lang !== undefined
    && messages[document.documentElement.lang] !== undefined ) {
  locale = document.documentElement.lang
}

let doc_url_root = DOCUMENTATION_OPTIONS.URL_ROOT;
if (doc_url_root == '#') {
    doc_url_root = '';
}

const path_static = `${doc_url_root}_static/`;

/**
 * Set up copy/paste for code blocks
 */

const runWhenDOMLoaded = cb => {
  if (document.readyState != 'loading') {
    cb()
  } else if (document.addEventListener) {
    document.addEventListener('DOMContentLoaded', cb)
  } else {
    document.attachEvent('onreadystatechange', function() {
      if (document.readyState == 'complete') cb()
    })
  }
}

const codeCellId = index => `codecell${index}`

// Clears selected text since ClipboardJS will select the text when copying
const clearSelection = () => {
  if (window.getSelection) {
    window.getSelection().removeAllRanges()
  } else if (document.selection) {
    document.selection.empty()
  }
}

// Changes tooltip text for two seconds, then changes it back
const temporarilyChangeTooltip = (el, oldText, newText) => {
  el.setAttribute('data-tooltip', newText)
  setTimeout(() => el.setAttribute('data-tooltip', oldText), 2000)
}

// Changes the copy button icon for two seconds, then changes it back
const temporarilyChangeIcon = (el) => {
  img = el.querySelector("img");
  img.setAttribute('src', `${path_static}check-solid.svg`)
  setTimeout(() => img.setAttribute('src', `${path_static}copy-button.svg`), 2000)
}

const addCopyButtonToCodeCells = () => {
  // If ClipboardJS hasn't loaded, wait a bit and try again. This
  // happens because we load ClipboardJS asynchronously.
  if (window.ClipboardJS === undefined) {
    setTimeout(addCopyButtonToCodeCells, 250)
    return
  }

  // Add copybuttons to all of our code cells
  const codeCells = document.querySelectorAll('div.highlight pre')
  codeCells.forEach((codeCell, index) => {
    const id = codeCellId(index)
    codeCell.setAttribute('id', id)
    const pre_bg = getComputedStyle(codeCell).backgroundColor;

    const clipboardButton = id =>
    `<button class="copybtn o-tooltip--left" style="background-color: ${pre_bg}" data-tooltip="${messages[locale]['copy']}" data-clipboard-target="#${id}">
      <img src="${path_static}copy-button.svg" alt="${messages[locale]['copy_to_clipboard']}">
    </button>`
    codeCell.insertAdjacentHTML('afterend', clipboardButton(id))
  })

function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // $& means the whole matched string
}

// Callback when a copy button is clicked. Will be passed the node that was clicked
// should then grab the text and replace pieces of text that shouldn't be used in output
function formatCopyText(textContent, copybuttonPromptText, isRegexp = false, onlyCopyPromptLines = true, removePrompts = true, copyEmptyLines = true, lineContinuationChar = "", hereDocDelim = "") {

    var regexp;
    var match;

    // Do we check for line continuation characters and "HERE-documents"?
    var useLineCont = !!lineContinuationChar
    var useHereDoc = !!hereDocDelim

    // create regexp to capture prompt and remaining line
    if (isRegexp) {
        regexp = new RegExp('^(' + copybuttonPromptText + ')(.*)')
    } else {
        regexp = new RegExp('^(' + escapeRegExp(copybuttonPromptText) + ')(.*)')
    }

    const outputLines = [];
    var promptFound = false;
    var gotLineCont = false;
    var gotHereDoc = false;
    const lineGotPrompt = [];
    for (const line of textContent.split('\n')) {
        match = line.match(regexp)
        if (match || gotLineCont || gotHereDoc) {
            promptFound = regexp.test(line)
            lineGotPrompt.push(promptFound)
            if (removePrompts && promptFound) {
                outputLines.push(match[2])
            } else {
                outputLines.push(line)
            }
            gotLineCont = line.endsWith(lineContinuationChar) & useLineCont
            if (line.includes(hereDocDelim) & useHereDoc)
                gotHereDoc = !gotHereDoc
        } else if (!onlyCopyPromptLines) {
            outputLines.push(line)
        } else if (copyEmptyLines && line.trim() === '') {
            outputLines.push(line)
        }
    }

    // If no lines with the prompt were found then just use original lines
    if (lineGotPrompt.some(v => v === true)) {
        textContent = outputLines.join('\n');
    }

    // Remove a trailing newline to avoid auto-running when pasting
    if (textContent.endsWith("\n")) {
        textContent = textContent.slice(0, -1)
    }
    return textContent
}


var copyTargetText = (trigger) => {
  var target = document.querySelector(trigger.attributes['data-clipboard-target'].value);
  return formatCopyText(target.innerText, '', false, true, true, true, '', '')
}

  // Initialize with a callback so we can modify the text before copy
  const clipboard = new ClipboardJS('.copybtn', {text: copyTargetText})

  // Update UI with error/success messages
  clipboard.on('success', event => {
    clearSelection()
    temporarilyChangeTooltip(event.trigger, messages[locale]['copy'], messages[locale]['copy_success'])
    temporarilyChangeIcon(event.trigger)
  })

  clipboard.on('error', event => {
    temporarilyChangeTooltip(event.trigger, messages[locale]['copy'], messages[locale]['copy_failure'])
  })
}

runWhenDOMLoaded(addCopyButtonToCodeCells)