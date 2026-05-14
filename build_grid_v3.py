#!/usr/bin/env python3
"""Финальный вариант: 15 слов с цитатами из лекции."""
import json, sys
from build_grid import empty_grid, can_place, place, unplace, find_placements, solve, GRID

WORDS_V3 = [
    ("СИНХРОСИГНАЛ", "Импульс, отличающийся от импульсов канальных интервалов; определяет начало цикла и обеспечивает правильное распределение дискретных отсчётов по каналам. (Слайд 6)"),
    ("РЕКОМБИНАЦИЯ", "Процесс соединения электронов и дырок в активном слое СИД, сопровождающийся излучением света. (Слайд 174)"),
    ("КОДИРОВАНИЕ",  "Преобразование квантованных отсчётов в соответствующие кодовые комбинации. (Слайд 8)"),
    ("КВАНТОВАНИЕ",  "Преобразование дискретных отсчётов сигнала в ближайшие разрешённые уровни. (Слайд 8)"),
    ("СВЕРХЦИКЛ",    "Минимальный интервал времени, за который передаётся один отсчёт каждого из 60 сигнальных каналов. (Слайд 46)"),
    ("ИНТЕРФЕЙС",    "Определённая стандартами граница взаимодействия различных устройств, представленная аппаратно-программными средствами. (Слайд 32)"),
    ("КОНТЕЙНЕР",    "Циклически повторяющаяся информационная структура, предназначенная для транспортировки в сети SDH стандартных цифровых потоков PDH. (Слайд 37)"),
    ("ТАЙМСЛОТ",     "Канальный интервал длительностью 3,906 мкс — один из 32 в цикле ИКМ-30. (Слайд 46)"),
    ("ДЕКОДЕР",      "Устройство для преобразования 8-разрядных кодовых комбинаций в амплитудные значения группового АИМ-сигнала. (Слайд 18)"),
    ("ВСТАВКА",      "Фиксированная остановка аппаратуры, во время которой в этот момент ничего не передаётся. (Слайд 118)"),
    ("КОЛЬЦО",       "Топология SDH-сети, основное преимущество которой — лёгкость организации защиты типа 1+1. (Слайд 87)"),
    ("ТРАКТ",        "Логическое соединение между точкой, в которой собирается виртуальный контейнер VC, и точкой, в которой он разбирается. (Слайд 37)"),
    ("ЛАЗЕР",        "Устройство, усиливающее вынужденное излучение активной среды. (Слайд 168)"),
    ("МЕТКА",        "Значение от 0 до 1 048 575, на основе которого LSR в сети MPLS принимает решение, что делать с пакетом. (Слайд 221)"),
    ("ЦИКЛ",         "Время, в течение которого однократно передаются все канальные интервалы объединённых каналов и синхросигнал. (Слайд 6)"),
]

def main():
    words_all = sorted(WORDS_V3, key=lambda x: -len(x[0]))
    best = None
    best_score = 999
    for seed in range(10):
        words = list(words_all)
        if seed > 0:
            words = words[seed:] + words[:seed]
        for target in [(7,8),(8,7),(6,9),(9,6),(15,15)]:
            g = empty_grid()
            placed = []
            result = solve(g, words, placed, target_h=target[0], target_v=target[1])
            if result and len(result) == 15:
                h_n = sum(1 for p in result if p['dir']=='h')
                v_n = sum(1 for p in result if p['dir']=='v')
                score = abs(h_n - 7) + abs(v_n - 8)
                if score < best_score:
                    best_score = score; best = result
                if score == 0: break
        if best_score == 0: break

    result = best
    if not result:
        print("FAILED", file=sys.stderr); sys.exit(1)

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
        placed_norm.append({'word':p['word'],'clue':p['clue'],'row':nr,'col':nc,'dir':p['dir']})
        for i, ch in enumerate(p['word']):
            if p['dir']=='h': grid_norm[nr][nc+i] = ch
            else: grid_norm[nr+i][nc] = ch

    h_n = sum(1 for p in placed_norm if p['dir']=='h')
    v_n = sum(1 for p in placed_norm if p['dir']=='v')
    print(f"V3: {rows}x{cols}, слов={len(placed_norm)}, H={h_n} V={v_n}\n")
    for row in grid_norm:
        print(' '.join((ch if ch else '·') for ch in row))
    print()
    for p in placed_norm:
        print(f"  {p['dir'].upper()} [{p['row']:2},{p['col']:2}] {p['word']}")
    out = {'rows':rows,'cols':cols,'grid':grid_norm,'words':placed_norm}
    open('/Users/timur/Downloads/mdk-crossword/grid_final.json','w',encoding='utf-8').write(
        json.dumps(out, ensure_ascii=False, indent=2)
    )
    print("\nСохранено: grid_final.json")

if __name__ == '__main__':
    main()
