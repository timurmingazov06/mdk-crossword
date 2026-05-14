#!/usr/bin/env python3
"""Генерирует print.html — версия кроссворда для печати на A4 (1 страница)."""
import json
from collections import defaultdict

DATA = json.load(open('/Users/timur/Downloads/mdk-crossword/grid_final.json', encoding='utf-8'))

rows = DATA['rows']
cols = DATA['cols']
grid = DATA['grid']
words = DATA['words']

# Нумерация: сортируем слова, начинающиеся слева-сверху → правее-ниже
words_sorted = sorted(words, key=lambda w: (w['row'], w['col']))
num_by_start = {}
counter = 0
for w in words_sorted:
    key = (w['row'], w['col'])
    if key not in num_by_start:
        counter += 1
        num_by_start[key] = counter
    w['num'] = num_by_start[key]

# Карта клетки → номер (если эта клетка стартовая для какого-то слова)
cell_num = {}
for w in words_sorted:
    key = (w['row'], w['col'])
    if key not in cell_num:
        cell_num[key] = w['num']

# Разделяем на горизонталь и вертикаль для подсказок
horiz = sorted([w for w in words_sorted if w['dir'] == 'h'], key=lambda w: w['num'])
verti = sorted([w for w in words_sorted if w['dir'] == 'v'], key=lambda w: w['num'])


def render_grid(show_answers: bool) -> str:
    """HTML сетки."""
    html = ['<div class="grid">']
    for r in range(rows):
        for c in range(cols):
            letter = grid[r][c]
            if letter is None:
                html.append('<div class="cell empty"></div>')
            else:
                cls = "cell letter"
                num = cell_num.get((r, c))
                content = ""
                if num:
                    content += f'<span class="num">{num}</span>'
                if show_answers:
                    content += f'<span class="letter-ans">{letter}</span>'
                html.append(f'<div class="{cls}">{content}</div>')
    html.append('</div>')
    return ''.join(html)


def render_clues(show_answers: bool) -> str:
    """HTML вопросов в две колонки."""
    def fmt(w):
        ans = f' <em>— {w["word"]}</em>' if show_answers else ''
        return f'<li><b>{w["num"]}.</b> {w["clue"]}{ans}</li>'

    h_html = '\n'.join(fmt(w) for w in horiz)
    v_html = '\n'.join(fmt(w) for w in verti)
    return f"""
<div class="clues">
  <div class="col">
    <h2>По горизонтали</h2>
    <ol>{h_html}</ol>
  </div>
  <div class="col">
    <h2>По вертикали</h2>
    <ol>{v_html}</ol>
  </div>
</div>
"""


CSS = """
@page { size: A4 portrait; margin: 8mm 10mm; }
html, body { background: white; color: #000; margin: 0; padding: 0; }
body {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 9pt; line-height: 1.3;
}
.page {
  width: 100%;
  max-width: 190mm;
  margin: 0 auto;
}
h1 {
  font-size: 13pt;
  text-align: center;
  margin: 0 0 1mm;
  font-weight: 700;
}
.sub {
  text-align: center;
  font-size: 8pt;
  color: #555;
  margin: 0 0 3mm;
  font-style: italic;
}
.field-row {
  font-size: 8pt;
  margin: 0 0 3mm;
}
.field-row span {
  display: inline-block;
  border-bottom: 0.4pt solid #000;
  min-width: 38mm;
  margin-right: 6mm;
  padding: 0 1mm;
}

/* ── Сетка ── */
.grid {
  display: grid;
  grid-template-columns: repeat(COLS, CELLmm);
  grid-auto-rows: CELLmm;
  margin: 0 auto 4mm;
  width: max-content;
}
.cell {
  position: relative;
  box-sizing: border-box;
  text-align: center;
}
.cell.letter {
  border: 0.5pt solid #000;
  background: #fff;
}
.cell.empty {
  border: 0.5pt dotted transparent;
}
.cell .num {
  position: absolute; top: 0.1mm; left: 0.4mm;
  font-size: 5pt; font-weight: 400; line-height: 1;
  font-family: Arial, sans-serif;
}
.cell .letter-ans {
  display: block;
  line-height: CELLmm;
  font-size: LETTERpt;
  font-weight: 700;
  font-family: Arial, sans-serif;
}

/* ── Вопросы ── */
.clues {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 5mm;
  font-size: 8.5pt;
  line-height: 1.28;
}
.clues .col h2 {
  font-size: 9pt;
  margin: 0 0 1.5mm;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  border-bottom: 0.5pt solid #000;
  padding-bottom: 0.5mm;
  font-weight: 700;
}
.clues ol {
  margin: 0;
  padding: 0;
  list-style: none;
}
.clues li {
  margin: 0 0 1mm;
  padding-left: 5mm;
  text-indent: -5mm;
  page-break-inside: avoid;
  break-inside: avoid;
}
.clues li b {
  font-weight: 700;
  display: inline-block;
  min-width: 4.5mm;
  text-indent: 0;
}
.clues li em {
  font-style: italic;
  color: #333;
  font-weight: 700;
}

/* Тулбар с кнопками — только на экране */
.toolbar {
  position: fixed; top: 8px; right: 8px;
  display: flex; gap: 6px;
  z-index: 100;
}
.toolbar a, .toolbar button {
  background: #1a1a1a; color: #fff;
  border: 1px solid #444;
  padding: 6px 12px; font-size: 12px;
  text-decoration: none; border-radius: 4px;
  font-family: Arial, sans-serif; cursor: pointer;
}
.toolbar a:hover, .toolbar button:hover { background: #333; }
.toolbar a.current { background: #fff; color: #000; }
@media print { .toolbar { display: none !important; } }
"""

# Высота клетки для сетки 18x22: займём ширину ~150-170mm
# Для cols=22, ширина ~170mm → клетка ~7.7mm. Возьмём 7.5mm.
CELL_MM = 7.5
LETTER_PT = 12

CSS_FILLED = (CSS
    .replace("COLS", str(cols))
    .replace("CELLmm", f"{CELL_MM}mm")
    .replace("LETTERpt", f"{LETTER_PT}pt")
)


def render_page(show_answers: bool, other_url: str, title_extra: str) -> str:
    body_grid = render_grid(show_answers)
    body_clues = render_clues(show_answers)
    toolbar = f"""
    <div class="toolbar">
      <button onclick="window.print()">Печать</button>
      <a href="./print.html" class="{'current' if not show_answers else ''}">Пустой</a>
      <a href="./print_answers.html" class="{'current' if show_answers else ''}">С ответами</a>
      <a href="./">Интерактив</a>
    </div>
    """
    field_row = "" if show_answers else """
    <div class="field-row">
      <span>Ф.И.О. ____________________</span>
      <span>Группа _______</span>
      <span>Дата _______</span>
    </div>
    """
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8" />
<title>МДК 02.02 · Кроссворд · {title_extra}</title>
<style>{CSS_FILLED}</style>
</head>
<body>
{toolbar}
<div class="page">
  <h1>МДК 02.02 · Кроссворд по транспортным сетям связи{(' — ответы' if show_answers else '')}</h1>
  <div class="sub">Все определения — прямые цитаты из лекции</div>
  {field_row}
  {body_grid}
  {body_clues}
</div>
</body>
</html>
"""


# Пустой бланк
open('/Users/timur/Downloads/mdk-crossword/print.html', 'w', encoding='utf-8').write(
    render_page(show_answers=False, other_url='print_answers.html', title_extra='бланк для печати')
)
# С ответами
open('/Users/timur/Downloads/mdk-crossword/print_answers.html', 'w', encoding='utf-8').write(
    render_page(show_answers=True, other_url='print.html', title_extra='с ответами')
)

print("Created:")
print("  /Users/timur/Downloads/mdk-crossword/print.html")
print("  /Users/timur/Downloads/mdk-crossword/print_answers.html")
print(f"  Grid: {rows}×{cols}, cells {CELL_MM}mm")
print(f"  Words: H={len(horiz)}, V={len(verti)}")
