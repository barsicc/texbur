#!/usr/bin/env bash
# Сборка ЛР4_защита.pdf из ЛР4_защита.md: pandoc (формулы → MathML) → Chromium (печать в PDF).
set -euo pipefail
cd "$(dirname "$0")/.."
TMP=$(mktemp -d)
cat > "$TMP/style.css" <<'CSS'
body { font-family: "DejaVu Serif", serif; font-size: 11pt; line-height: 1.4; max-width: 100%; margin: 0; color: #111; }
h1 { font-size: 17pt; margin: 0 0 4pt; }
h2 { font-size: 13.5pt; margin: 14pt 0 4pt; border-bottom: 1px solid #999; break-after: avoid; }
h3 { font-size: 12pt; }
math { font-size: 1.08em; }
math[display="block"] { display: block math; margin: 6pt 0; break-inside: avoid; page-break-inside: avoid; }
table { border-collapse: collapse; margin: 6pt 0; }
th, td { border: 1px solid #aaa; padding: 2pt 6pt; vertical-align: middle; }
img { max-width: 92%; display: block; margin: 6pt auto; break-inside: avoid; }
figure { margin: 0; break-inside: avoid; }
figcaption { text-align: center; font-size: 9.5pt; color: #444; }
code { font-size: 9.5pt; }
hr { border: 0; border-top: 1px solid #ccc; }
CSS
pandoc -f markdown+lists_without_preceding_blankline ЛР4_защита.md -s --mathml --css "$TMP/style.css" \
  --metadata title="ЛР №4 — ответы на защиту" --metadata pagetitle="ЛР4 защита" \
  -V title= -o ._build.html
# убрать пустой заголовок, который pandoc вставляет из title
sed -i 's#<header id="title-block-header">.*</header>##' ._build.html
/opt/pw-browsers/chromium-1194/chrome-linux/chrome --headless --no-sandbox --disable-gpu \
  --no-pdf-header-footer --print-to-pdf="ЛР4_защита.pdf" "file://$PWD/._build.html" 2>/dev/null
rm -rf "$TMP" ._build.html
echo "OK: ЛР4_защита.pdf"
