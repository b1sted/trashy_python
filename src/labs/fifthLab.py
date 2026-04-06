"""
Лабораторная работа 5
Решение задач оптимизации методом динамического программирования

Находит наиболее экономный маршрут из пункта 1 в пункт 10
на региональной сети дорог (рис. 5.2 методички), а также
оптимальные маршруты из всех остальных пунктов в пункт 10.

Структура сети (рис. 5.2):
  Группа I:   {1}
  Группа II:  {2, 3, 4}
  Группа III: {5, 6, 7}
  Группа IV:  {8, 9}
  Группа V:   {10}

  Шаг 1: 1 → 2, 3, 4
  Шаг 2: 2 → 5, 7
         3 → 5, 6, 7
         4 → 5, 6, 7
  Шаг 3: 5 → 8, 9
         6 → 8, 9
         7 → 9
  Шаг 4: 8 → 10
         9 → 10
"""

from pathlib import Path

# ─────────────────────────────────────────────
#  Таблица тарифов (табл. 5.6 методички)
# ─────────────────────────────────────────────

TARIFF_TABLE = {
    'C12':  [7, 4, 9, 1, 5, 8, 3, 6, 1, 4, 2, 4, 5, 3, 3],
    'C13':  [3, 8, 2, 6, 3, 1, 5, 2, 9, 6, 5, 6, 2, 5, 5],
    'C14':  [5, 4, 5, 2, 8, 5, 4, 6, 3, 1, 7, 7, 4, 7, 6],
    'C25':  [2, 6, 3, 5, 2, 9, 1, 7, 8, 3, 9, 8, 6, 9, 4],
    'C27':  [7, 1, 7, 3, 5, 2, 6, 3, 7, 5, 4, 4, 7, 2, 3],
    'C35':  [9, 9, 4, 6, 8, 6, 2, 9, 4, 7, 6, 6, 8, 5, 7],
    'C36':  [3, 3, 6, 8, 1, 8, 7, 2, 9, 3, 2, 7, 1, 8, 9],
    'C37':  [1, 5, 8, 4, 7, 4, 4, 8, 3, 6, 1, 8, 4, 1, 4],
    'C45':  [8, 4, 1, 7, 5, 5, 6, 5, 7, 2, 3, 2, 5, 4, 6],
    'C46':  [4, 8, 3, 2, 9, 2, 8, 2, 4, 5, 5, 1, 7, 8, 7],
    'C47':  [5, 2, 5, 9, 1, 6, 3, 9, 8, 9, 2, 8, 8, 3, 4],
    'C58':  [2, 7, 8, 5, 3, 1, 7, 4, 6, 1, 6, 9, 5, 5, 3],
    'C59':  [6, 4, 7, 3, 5, 8, 2, 6, 3, 8, 7, 3, 3, 7, 1],
    'C68':  [1, 9, 1, 6, 8, 3, 9, 7, 1, 2, 8, 5, 4, 9, 2],
    'C69':  [9, 6, 4, 1, 4, 6, 2, 4, 8, 3, 2, 7, 1, 1, 3],
    'C79':  [4, 1, 5, 4, 9, 2, 8, 6, 9, 5, 6, 3, 4, 3, 4],
    'C810': [3, 7, 9, 6, 2, 5, 1, 7, 1, 3, 7, 2, 5, 2, 5],
    'C910': [8, 2, 5, 1, 7, 9, 3, 6, 4, 8, 9, 3, 9, 1, 8],
}

VARIANTS = {
    v: {k: TARIFF_TABLE[k][v - 1] for k in TARIFF_TABLE}
    for v in range(1, 16)
}

# Рёбра по шагам
STEP_EDGES = {
    4: [(8, 10), (9, 10)],
    3: [(5, 8), (5, 9), (6, 8), (6, 9), (7, 9)],
    2: [(2, 5), (2, 7), (3, 5), (3, 6), (3, 7), (4, 5), (4, 6), (4, 7)],
    1: [(1, 2), (1, 3), (1, 4)],
}

STEP_LABEL = {
    4: 'IV → V   ({8,9} → {10})',
    3: 'III → IV ({5,6,7} → {8,9})',
    2: 'II → III ({2,3,4} → {5,6,7})',
    1: 'I → II   ({1} → {2,3,4})',
}


# ─────────────────────────────────────────────
#  Вспомогательные функции
# ─────────────────────────────────────────────

def edge_cost(c, i, j):
    """Тариф перевозки по ребру i→j."""
    return c[f'C{i}{j}']


def get_path(start, next_opt):
    """Восстановить оптимальный маршрут из пункта start в пункт 10."""
    path = [start]
    node = start
    while node != 10:
        node = next_opt[node]
        path.append(node)
    return path


# ─────────────────────────────────────────────
#  Алгоритм ДП
# ─────────────────────────────────────────────

def solve(c):
    """
    Условная оптимизация (обратный проход).

    Возвращает:
      F         — словарь минимальных затрат из каждого узла до 10
      next_opt  — словарь оптимального следующего узла
      step_data — данные по каждому шагу для построения отчёта
    """
    F = {10: 0}
    next_opt = {}
    step_data = {}

    for step in [4, 3, 2, 1]:
        edges = STEP_EDGES[step]
        sources = sorted(set(i for i, j in edges))
        rows = []

        for src in sources:
            dests = [j for i, j in edges if i == src]
            best_cost = None
            best_dest = None
            opts = []

            for dst in dests:
                z = edge_cost(c, src, dst)
                f_next = F[dst]
                total = z + f_next
                opts.append((src, dst, z, f_next, total))
                if best_cost is None or total < best_cost:
                    best_cost = total
                    best_dest = dst

            F[src] = best_cost
            next_opt[src] = best_dest
            rows.append((src, opts, best_cost, best_dest))

        step_data[step] = rows

    return F, next_opt, step_data


# ─────────────────────────────────────────────
#  Построение отчёта
# ─────────────────────────────────────────────

def build_report(variant, c, F, next_opt, step_data):
    W = 72
    L = []

    def sep():  L.append('-' * W)
    def dsep(): L.append('=' * W)

    def hdr(t):
        L.append('')
        sep()
        L.append(t)
        sep()
        L.append('')

    dsep()
    L.append(f"{'Лабораторная работа 5':^{W}}")
    L.append(f"{'Решение задач оптимизации методом':^{W}}")
    L.append(f"{'динамического программирования':^{W}}")
    dsep()

    # ── Пункт 1. Исходные данные ──────────────────────────────────────
    hdr('Пункт 1. Исходные данные')
    L.append(f'  Вариант № {variant}')
    L.append('  Маршрут: из пункта 1 в пункт 10')
    L.append('')
    L.append('  Структура сети (рис. 5.2 методички):')
    L.append('    Шаг 1: 1 → {2,3,4}')
    L.append('    Шаг 2: {2,3,4} → {5,6,7}')
    L.append('    Шаг 3: {5,6,7} → {8,9}')
    L.append('    Шаг 4: {8,9} → {10}')
    L.append('')
    L.append('  Тарифы перевозки:')
    L.append('')

    sections = [
        ('Шаг 1', [(1,2),(1,3),(1,4)]),
        ('Шаг 2', [(2,5),(2,7),(3,5),(3,6),(3,7),(4,5),(4,6),(4,7)]),
        ('Шаг 3', [(5,8),(5,9),(6,8),(6,9),(7,9)]),
        ('Шаг 4', [(8,10),(9,10)]),
    ]
    for name, edges in sections:
        parts = ', '.join(f'c({i},{j})={edge_cost(c,i,j)}' for i, j in edges)
        L.append(f'    {name}: {parts}')
    L.append('')

    # ── Пункт 2. Условная оптимизация (обратный проход) ───────────────
    hdr('Пункт 2. Условная оптимизация (обратный проход)')
    L.append('  Функциональное уравнение Беллмана:')
    L.append('    F_i(x) = min{ z_i(x→u) + F_{i+1}(u) }')
    L.append(f'  Граничное условие: F(10) = 0')
    L.append('')

    for step in [4, 3, 2, 1]:
        L.append(f'  ── Шаг {step}: {STEP_LABEL[step]} {"─"*(30 - len(STEP_LABEL[step]))}')
        if step == 4:
            L.append('  F4(x) = min{ z4(x→u) }  (следующий пункт = 10, F(10)=0)')
        else:
            L.append(f'  F{step}(x) = min{{ z{step}(x→u) + F{step+1}(u) }}')
        L.append('')

        rows = step_data[step]
        for src, opts, best_cost, best_dest in rows:
            L.append(f'    Пункт {src}:')
            for (i, j, z, f_next, total) in opts:
                marker = '  ← min' if j == best_dest else ''
                if step == 4:
                    L.append(
                        f'      ({i}→{j}): z={z:2d}{marker}'
                    )
                else:
                    L.append(
                        f'      ({i}→{j}): z={z:2d},  '
                        f'F{step+1}({j})={f_next:2d},  '
                        f'сумма={total:2d}{marker}'
                    )
            L.append(f'      → F{step}({src}) = {best_cost},  '
                     f'оптимальный следующий: {best_dest}')
            L.append('')

    # ── Пункт 3. Безусловная оптимизация (прямой проход) ──────────────
    hdr('Пункт 3. Безусловная оптимизация (прямой проход)')
    L.append('  Восстанавливаем оптимальный маршрут из пункта 1 в пункт 10:')
    L.append('')

    path = get_path(1, next_opt)
    for idx in range(len(path) - 1):
        i, j = path[idx], path[idx + 1]
        nxt = next_opt.get(i, '—')
        L.append(f'    Шаг {idx+1}: из {i} → оптимальный следующий = {nxt}')

    L.append('')
    path_str = ' → '.join(str(p) for p in path)
    L.append(f'  Оптимальный маршрут: {path_str}')
    L.append('')

    L.append('  Детализация затрат по маршруту:')
    running = 0
    for idx in range(len(path) - 1):
        i, j = path[idx], path[idx + 1]
        z = edge_cost(c, i, j)
        running += z
        L.append(f'    {i} → {j}:  c({i},{j}) = {z}')
    L.append('')
    L.append(f'  Минимальные транспортные затраты: {F[1]}')

    # ── Пункт 4. Оптимальные маршруты из всех пунктов ─────────────────
    hdr('Пункт 4. Оптимальные маршруты из всех пунктов сети в пункт 10')

    hline = f"  +{'─'*4}+{'─'*12}+{'─'*30}+{'─'*10}+"
    L.append(hline)
    L.append(
        f"  | {'№':^2} | {'Из пункта':^10} | "
        f"{'Оптимальный маршрут':^28} | {'Затраты':^8} |"
    )
    L.append(hline)

    for num, start in enumerate(range(1, 10), start=1):
        p = get_path(start, next_opt)
        p_str = ' → '.join(str(x) for x in p)
        cost = F[start]
        L.append(
            f"  | {num:^2} | {start:^10} | {p_str:<28} | {cost:^8} |"
        )

    L.append(hline)
    L.append('')
    dsep()
    L.append('Все расчёты выполнены.')
    dsep()

    return '\n'.join(L)


# ─────────────────────────────────────────────
#  Главная функция
# ─────────────────────────────────────────────

def main():
    print('=' * 72)
    print('  ЛАБОРАТОРНАЯ РАБОТА № 5')
    print('  Решение задач оптимизации методом динамического программирования')
    print('=' * 72)

    while True:
        raw = input('\nВведите номер варианта (1–15): ').strip()
        try:
            choice = int(raw)
            if 1 <= choice <= 15:
                break
            print('  Пожалуйста, введите число от 1 до 15.')
        except ValueError:
            print('  Введите целое число.')

    c = VARIANTS[choice]
    print(f'\n[!] Загружены тарифы для варианта {choice}.')

    F, next_opt, step_data = solve(c)

    report = build_report(choice, c, F, next_opt, step_data)
    print('\n' + report)

    project_root = Path(__file__).parent.parent.parent
    out_dir = project_root / 'output' / 'fifthLab'
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f'Lab_rabota_5_stud_N{choice}.txt'

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report + '\n')
    print(f'\n[✓] Результаты сохранены в файл: {out_path}')


if __name__ == '__main__':
    main()