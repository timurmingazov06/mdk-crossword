#!/usr/bin/env python3
"""Жадный + backtracking генератор кроссворда для 15 слов."""

import json
import sys
from copy import deepcopy

WORDS = [
    ("МУЛЬТИПЛЕКСОР", "Устройство, объединяющее несколько входных цифровых потоков в один групповой сигнал с большей пропускной способностью."),
    ("ДИСКРЕТИЗАЦИЯ", "Преобразование непрерывного во времени аналогового сигнала в последовательность мгновенных отсчётов через равные промежутки времени."),
    ("РЕГЕНЕРАТОР",  "Устройство, полностью восстанавливающее форму, амплитуду и временные позиции импульсов искажённого цифрового сигнала."),
    ("КОТЕЛЬНИКОВ",  "Советский учёный, сформулировавший теорему о минимальной частоте дискретизации сигнала с ограниченным спектром."),
    ("КВАНТОВАНИЕ",  "Процесс замены непрерывных значений отсчётов аналогового сигнала ближайшими разрешёнными дискретными уровнями."),
    ("КОНТЕЙНЕР",    "Структурный элемент кадра SDH (VC-12, VC-4), переносящий полезную нагрузку пользователя вместе с трактовым заголовком."),
    ("ДИСПЕРСИЯ",    "Уширение оптического импульса при распространении по волокну из-за разной скорости спектральных компонент сигнала."),
    ("УСИЛИТЕЛЬ",    "Оптический прибор (EDFA) на основе активного волокна, увеличивающий мощность сигнала без преобразования в электрическую форму."),
    ("ЗАГОЛОВОК",    "Служебная часть кадра STM-N (SOH/POH), несущая информацию для управления, контроля ошибок и синхронизации."),
    ("ВОЛОКНО",      "Тонкая нить из кварцевого стекла, направляющая световой сигнал в ВОСП за счёт полного внутреннего отражения."),
    ("ДЖИТТЕР",      "Кратковременное случайное отклонение фронтов цифровых импульсов от их идеальных временных позиций."),
    ("КОЛЬЦО",       "Топология SDH-сети, в которой узлы соединены замкнутым контуром, обеспечивая 100% резервирование тракта."),
    ("ЛАЗЕР",        "Полупроводниковый источник когерентного монохроматического оптического излучения в передатчиках DWDM."),
    ("МЕТКА",        "Короткий идентификатор фиксированной длины в заголовке пакета, по которому маршрутизатор MPLS принимает решение о коммутации."),
    ("ЭРБИЙ",        "Редкоземельный химический элемент, ионами которого легируют активное волокно оптического усилителя WDM."),
]

GRID = 24

def empty_grid():
    return [[None]*GRID for _ in range(GRID)]

def can_place(g, word, r, c, d):
    n = len(word)
    if d == 'h':
        if c < 0 or c + n > GRID or r < 0 or r >= GRID: return False
        if c > 0 and g[r][c-1] is not None: return False
        if c+n < GRID and g[r][c+n] is not None: return False
    else:
        if r < 0 or r + n > GRID or c < 0 or c >= GRID: return False
        if r > 0 and g[r-1][c] is not None: return False
        if r+n < GRID and g[r+n][c] is not None: return False
    crossings = 0
    for i, ch in enumerate(word):
        if d == 'h':
            rr, cc = r, c+i
        else:
            rr, cc = r+i, c
        ex = g[rr][cc]
        if ex is None:
            if d == 'h':
                if rr > 0 and g[rr-1][cc] is not None: return False
                if rr+1 < GRID and g[rr+1][cc] is not None: return False
            else:
                if cc > 0 and g[rr][cc-1] is not None: return False
                if cc+1 < GRID and g[rr][cc+1] is not None: return False
        else:
            if ex != ch: return False
            crossings += 1
    return crossings  # 0 для самого первого; для остальных >0 проверим снаружи

def place(g, word, r, c, d):
    cells = []
    for i, ch in enumerate(word):
        if d == 'h':
            rr, cc = r, c+i
        else:
            rr, cc = r+i, c
        cells.append((rr, cc, g[rr][cc] is None))
        g[rr][cc] = ch
    return cells

def unplace(g, cells):
    for rr, cc, was_empty in cells:
        if was_empty:
            g[rr][cc] = None

def find_placements(g, word, placed):
    """Возвращает все валидные позиции, требующие хотя бы 1 пересечения."""
    results = []
    seen = set()
    for p in placed:
        pw, pr, pc, pd = p['word'], p['row'], p['col'], p['dir']
        for j, pch in enumerate(pw):
            for i, ch in enumerate(word):
                if ch == pch:
                    if pd == 'h':
                        nr, nc, nd = pr - i, pc + j, 'v'
                    else:
                        nr, nc, nd = pr + j, pc - i, 'h'
                    key = (nr, nc, nd)
                    if key in seen: continue
                    seen.add(key)
                    cr = can_place(g, word, nr, nc, nd)
                    if cr is False or cr == 0: continue
                    results.append((cr, nr, nc, nd))
    results.sort(key=lambda x: -x[0])
    return [(r, c, d) for _, r, c, d in results]

def solve(g, remaining, placed, target_h=7, target_v=8):
    if not remaining:
        h_count = sum(1 for p in placed if p['dir']=='h')
        v_count = sum(1 for p in placed if p['dir']=='v')
        # Соблюсти ровно 7H/8V желательно, но не обязательно
        return placed

    # Не первое слово
    if placed:
        # Сначала пробуем слова с минимальным числом вариантов (most constrained)
        candidates = []
        for word, clue in remaining:
            opts = find_placements(g, word, placed)
            candidates.append((len(opts), word, clue, opts))
        candidates.sort()
        for _, word, clue, opts in candidates:
            if not opts: continue
            for r, c, d in opts:
                # Проверим, не нарушит ли это балансировку 7H/8V
                h_count = sum(1 for p in placed if p['dir']=='h')
                v_count = sum(1 for p in placed if p['dir']=='v')
                if d == 'h' and h_count >= target_h:
                    # Можно, но прорейтингуем: пропустим если есть выбор
                    continue
                if d == 'v' and v_count >= target_v:
                    continue
                cells = place(g, word, r, c, d)
                placed.append({'word': word, 'clue': clue, 'row': r, 'col': c, 'dir': d})
                new_remaining = [(w,c2) for w,c2 in remaining if w != word]
                res = solve(g, new_remaining, placed, target_h, target_v)
                if res: return res
                placed.pop()
                unplace(g, cells)
            # Если строгий target не сработал — попробуем без ограничения
            for r, c, d in opts:
                cells = place(g, word, r, c, d)
                placed.append({'word': word, 'clue': clue, 'row': r, 'col': c, 'dir': d})
                new_remaining = [(w,c2) for w,c2 in remaining if w != word]
                res = solve(g, new_remaining, placed, target_h, target_v)
                if res: return res
                placed.pop()
                unplace(g, cells)
            return None
        return None
    else:
        # Первое слово — самое длинное, кладём горизонтально в центр
        word, clue = remaining[0]
        n = len(word)
        r = GRID // 2
        c = (GRID - n) // 2
        cells = place(g, word, r, c, 'h')
        placed.append({'word': word, 'clue': clue, 'row': r, 'col': c, 'dir': 'h'})
        new_remaining = remaining[1:]
        res = solve(g, new_remaining, placed, target_h, target_v)
        if res: return res
        placed.pop()
        unplace(g, cells)
        return None

def main():
    # Перебираем разные стартовые порядки чтобы получить ровно 7H/8V
    import itertools
    words_all = sorted(WORDS, key=lambda x: -len(x[0]))
    best = None
    best_score = 999
    # Пробуем несколько перестановок верхушки списка
    for seed in range(8):
        words = list(words_all)
        # Смещаем порядок
        if seed > 0:
            words = words[seed:] + words[:seed]
        for target in [(7, 8), (8, 7), (6, 9), (9, 6), (15, 15)]:
            g = empty_grid()
            placed = []
            result = solve(g, words, placed, target_h=target[0], target_v=target[1])
            if result and len(result) == 15:
                h_n = sum(1 for p in result if p['dir']=='h')
                v_n = sum(1 for p in result if p['dir']=='v')
                score = abs(h_n - 7) + abs(v_n - 8)
                if score < best_score:
                    best_score = score
                    best = result
                if score == 0:
                    break
        if best_score == 0:
            break

    result = best
    if not result:
        print("FAILED", file=sys.stderr)
        sys.exit(1)

    # Нормализуем сетку: найдём bbox и сдвинем
    min_r = min(p['row'] for p in result)
    max_r = max(p['row'] + (len(p['word']) if p['dir']=='v' else 1) - 1 for p in result)
    min_c = min(p['col'] for p in result)
    max_c = max(p['col'] + (len(p['word']) if p['dir']=='h' else 1) - 1 for p in result)

    rows = max_r - min_r + 1
    cols = max_c - min_c + 1

    grid_norm = [[None]*cols for _ in range(rows)]
    placed_norm = []
    for p in result:
        nr, nc = p['row'] - min_r, p['col'] - min_c
        placed_norm.append({
            'word': p['word'],
            'clue': p['clue'],
            'row': nr,
            'col': nc,
            'dir': p['dir'],
        })
        for i, ch in enumerate(p['word']):
            if p['dir']=='h':
                grid_norm[nr][nc+i] = ch
            else:
                grid_norm[nr+i][nc] = ch

    # Печать
    print(f"Размер: {rows}x{cols}, слов: {len(placed_norm)}")
    h_n = sum(1 for p in placed_norm if p['dir']=='h')
    v_n = sum(1 for p in placed_norm if p['dir']=='v')
    print(f"Горизонталь: {h_n}, Вертикаль: {v_n}")
    print()
    for row in grid_norm:
        print(' '.join((ch if ch else '·') for ch in row))
    print()
    for p in placed_norm:
        print(f"  {p['dir'].upper()} [{p['row']:2},{p['col']:2}] {p['word']}")

    out = {
        'rows': rows,
        'cols': cols,
        'grid': grid_norm,
        'words': placed_norm,
    }
    with open('/Users/timur/Downloads/mdk-crossword/grid.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\nСохранено: /Users/timur/Downloads/mdk-crossword/grid.json")

if __name__ == '__main__':
    main()
