"""
Лабораторная работа 4
Оптимизация работ методом сетевого планирования и управления

Вычисляет:
  1. Ранние сроки свершения событий  (прямой проход)
  2. Поздние сроки свершения событий (обратный проход)
  3. Резервы времени событий
  4. Критический путь и длину критического пути
"""

from pathlib import Path
from collections import defaultdict, deque

# ─────────────────────────────────────────────
#  База данных вариантов (Рёбра: откуда, куда, время)
# ─────────────────────────────────────────────

EXAMPLE_EDGES = [
    (1, 2, 10), (1, 3, 5), (1, 4, 4),
    (2, 4,  1), (2, 5, 6),
    (3, 4,  8), (3, 6, 0),
    (4, 5,  2), (4, 6, 4), (4, 7, 5),
    (5, 7,  8),
    (6, 7, 10),
]

VARIANTS = {
    0: EXAMPLE_EDGES,

    1: [
        (1, 2, 7), (1, 3, 5), (2, 4, 9), (2, 5, 2), (3, 5, 4),
        (3, 6, 8), (4, 7, 5), (5, 7, 6), (5, 8, 2), (6, 8, 5),
        (6, 9, 9), (7, 10, 7), (8, 10, 8), (8, 9, 7), (9, 10, 9)
    ],

    2: [
        (1, 2, 7), (1, 4, 4), (1, 3, 9), (2, 5, 5), (2, 8, 6),
        (3, 4, 5), (3, 6, 8), (4, 5, 8), (4, 7, 9), (5, 8, 2),
        (6, 7, 5), (7, 8, 6), (7, 9, 3), (8, 9, 8)
    ],

    3: [
        (1, 4, 5), (1, 7, 9), (1, 2, 2), (4, 3, 6), (4, 5, 8),
        (7, 4, 4), (7, 5, 5), (7, 9, 7), (2, 7, 3), (2, 9, 8),
        (2, 8, 4), (3, 10, 6), (5, 10, 3), (5, 9, 5), (9, 10, 9),
        (8, 9, 2)
    ],

    4: [
        (1, 4, 7), (1, 9, 4), (1, 3, 8), (4, 5, 5), (4, 2, 9),
        (9, 2, 6), (9, 6, 4), (3, 6, 8), (5, 8, 3), (2, 7, 2),
        (2, 6, 7), (6, 9, 5), (8, 7, 8), (7, 9, 6)
    ],

    5: [
        (1, 2, 7), (1, 5, 4), (1, 3, 5), (2, 4, 4), (2, 8, 7),
        (5, 4, 8), (5, 6, 5), (5, 9, 3), (3, 6, 6), (3, 8, 9),
        (4, 7, 7), (6, 9, 4), (8, 9, 8), (7, 9, 9)
    ],

    6: [
        (1, 4, 4), (1, 7, 5), (1, 2, 2), (4, 3, 3), (4, 5, 9),
        (7, 5, 7), (7, 8, 5), (2, 8, 6), (3, 8, 2), (5, 10, 6),
        (5, 6, 5), (8, 6, 8), (10, 9, 8), (6, 9, 9)
    ],

    7: [
        (1, 2, 4), (1, 4, 7), (1, 5, 5), (2, 6, 6), (2, 4, 2),
        (4, 6, 9), (4, 8, 8), (5, 8, 6), (5, 7, 4), (6, 7, 5),
        (8, 10, 5), (8, 9, 3), (7, 9, 7), (10, 9, 9)
    ],

    8: [
        (1, 2, 2), (1, 5, 7), (1, 3, 9), (2, 6, 8), (2, 5, 9),
        (5, 6, 5), (5, 8, 4), (3, 5, 5), (3, 4, 7), (6, 8, 2),
        (8, 9, 6), (8, 4, 7), (4, 9, 3), (4, 9, 4)
    ],

    9: [
        (1, 2, 7), (1, 4, 4), (1, 3, 9), (2, 5, 5), (2, 6, 6),
        (4, 5, 3), (4, 7, 2), (3, 7, 8), (3, 5, 4), (5, 6, 2),
        (5, 9, 9), (7, 9, 7), (7, 10, 4), (6, 9, 9), (9, 10, 10)
    ],

    10: [
        (1, 2, 6), (1, 5, 2), (1, 3, 4), (2, 4, 8), (2, 5, 9),
        (5, 4, 7), (5, 8, 8), (3, 5, 5), (3, 7, 7), (4, 9, 9),
        (4, 8, 3), (8, 10, 4), (8, 6, 5), (7, 6, 6), (9, 10, 2),
        (6, 7, 7)
    ],

    11: [
        (1, 2, 3), (1, 4, 7), (1, 3, 4), (2, 6, 6), (2, 5, 5),
        (4, 6, 9), (4, 8, 6), (3, 5, 2), (3, 7, 7), (6, 10, 8),
        (5, 8, 9), (5, 9, 8), (7, 9, 5), (8, 11, 3), (9, 11, 9)
    ],

    12: [
        (1, 2, 2), (1, 7, 7), (1, 3, 1), (2, 4, 4), (2, 5, 9),
        (7, 5, 3), (7, 8, 9), (3, 5, 5), (3, 6, 4), (4, 11, 7),
        (5, 8, 2), (5, 10, 5), (6, 9, 6), (8, 11, 2), (10, 11, 4),
        (9, 10, 2)
    ],

    13: [
        (1, 2, 4), (1, 3, 2), (1, 4, 7), (2, 5, 5), (2, 7, 3),
        (3, 7, 2), (3, 6, 4), (4, 6, 3), (4, 8, 8), (7, 5, 8),
        (7, 9, 7), (6, 9, 8), (5, 9, 5), (9, 8, 8)
    ],

    14: [
        (1, 2, 2), (1, 5, 7), (1, 3, 4), (2, 4, 8), (2, 5, 5),
        (5, 4, 4), (5, 7, 7), (3, 6, 9), (4, 7, 5), (7, 8, 8),
        (6, 8, 6), (6, 9, 5), (7, 10, 6), (8, 10, 10), (9, 10, 9)
    ],

    15: [
        (1, 2, 9), (1, 4, 4), (1, 3, 2), (2, 6, 2), (2, 5, 6),
        (4, 5, 1), (4, 7, 3), (3, 7, 4), (6, 10, 5), (5, 8, 7),
        (5, 9, 8), (7, 9, 5), (8, 10, 10), (9, 10, 9)
    ],

    16: [
        (1, 2, 7),  (1, 3, 4),  (1, 6, 5), (1, 7, 9),
        (2, 4, 4),  (2, 7, 2),
        (3, 5, 8),  (3, 6, 2),
        (4, 7, 3),  (4, 8, 7),
        (5, 6, 6),  (5, 9, 4),
        (6, 7, 9),  (6, 9, 2),  (6, 11, 3),
        (7, 8, 0),  (7, 10, 2), (7, 11, 8),
        (8, 10, 4), (9, 11, 5), (10, 11, 6)
    ],
}

# ─────────────────────────────────────────────
#  Вспомогательная функция: найти исходное и завершающее события
# ─────────────────────────────────────────────

def find_source_and_sink(edges):
    """
    Исходное событие — вершина без входящих рёбер.
    Завершающее событие — вершина без исходящих рёбер.
    """
    all_nodes   = set()
    has_incoming = set()
    has_outgoing = set()
    for i, j, _ in edges:
        all_nodes.add(i)
        all_nodes.add(j)
        has_outgoing.add(i)
        has_incoming.add(j)

    sources = sorted(all_nodes - has_incoming)   # нет входящих
    sinks   = sorted(all_nodes - has_outgoing)   # нет исходящих

    if len(sources) != 1:
        raise ValueError(f"Ожидается ровно одно исходное событие, найдено: {sources}")
    if len(sinks) != 1:
        raise ValueError(f"Ожидается ровно одно завершающее событие, найдено: {sinks}")

    return sources[0], sinks[0]


# ─────────────────────────────────────────────
#  Алгоритмы
# ─────────────────────────────────────────────

def topological_sort(all_nodes, edges):
    """Топологическая сортировка (алгоритм Кана)."""
    in_deg = {v: 0 for v in all_nodes}
    adj    = defaultdict(list)
    for i, j, _ in edges:
        adj[i].append(j)
        in_deg[j] += 1

    queue = deque(v for v in sorted(all_nodes) if in_deg[v] == 0)
    order = []
    while queue:
        v = queue.popleft()
        order.append(v)
        for u in sorted(adj[v]):
            in_deg[u] -= 1
            if in_deg[u] == 0:
                queue.append(u)
    return order


def compute_early(all_nodes, edges, topo_order):
    """Ранние сроки: tр(j) = max[tр(i) + t(i,j)]."""
    preds = defaultdict(list)
    for i, j, t in edges:
        preds[j].append((i, t))

    early = {v: 0 for v in all_nodes}
    for j in topo_order:
        if preds[j]:
            early[j] = max(early[i] + t for i, t in preds[j])
    return early


def compute_late(all_nodes, edges, early, topo_order, sink):
    """Поздние сроки: tп(i) = min[tп(j) - t(i,j)]."""
    succs = defaultdict(list)
    for i, j, t in edges:
        succs[i].append((j, t))

    late = {v: 0 for v in all_nodes}
    late[sink] = early[sink]          # граничное условие: завершающее событие

    for i in reversed(topo_order):
        if succs[i]:
            late[i] = min(late[j] - t for j, t in succs[i])
        elif i == sink:
            late[i] = early[sink]
    return late


def compute_reserves(all_nodes, early, late):
    """R(j) = tп(j) - tр(j)."""
    return {j: late[j] - early[j] for j in all_nodes}


def find_critical_path(edges, early, late):
    """
    Критические события: R(j) = 0.
    Критические работы: tп(j) - tр(i) - t(i,j) = 0.
    """
    reserves  = {j: late[j] - early[j] for j in early}
    crit_ev   = sorted(j for j in reserves if reserves[j] == 0)
    crit_ed   = [(i, j, t) for i, j, t in edges
                 if late[j] - early[i] - t == 0]
    return crit_ev, crit_ed


# ─────────────────────────────────────────────
#  Построение отчёта
# ─────────────────────────────────────────────

def build_report(variant, all_nodes, edges, early, late, reserves,
                 crit_ev, crit_ed, source, sink):
    W = 72
    L = []

    def sep():   L.append("-" * W)
    def dsep():  L.append("=" * W)
    def hdr(t):
        L.append("")
        sep()
        L.append(t)
        sep()
        L.append("")

    dsep()
    L.append(f"{'Лабораторная работа 4':^{W}}")
    L.append(f"{'Оптимизация работ методом сетевого планирования':^{W}}")
    dsep()

    # 1. Исходные данные
    hdr("Пункт 1. Исходные данные")
    if variant == 0:
        L.append("  Источник: Пример 4.1, рис. 4.3 методички")
    else:
        L.append(f"  Вариант № {variant}")
    L.append(f"  Число событий (вершин): {len(all_nodes)}")
    L.append(f"  Исходное событие: {source}    "
             f"Завершающее событие: {sink}")
    L.append("")
    L.append("  Перечень работ (рёбер) сети:")
    L.append("")
    for i, j, t in sorted(edges):
        tag = "  ← фиктивная работа" if t == 0 else ""
        L.append(f"    ({i},{j}):  t({i},{j}) = {t}{tag}")

    # 2. Ранние сроки
    hdr("Пункт 2. Ранние сроки свершения событий (прямой проход)")
    L.append("  Формула: tр(j) = max[ tр(i) + t(i,j) ]  для всех i → j")
    L.append(f"  Начальное условие: tр({source}) = 0")
    L.append("")
    preds = defaultdict(list)
    for i, j, t in edges:
        preds[j].append((i, t))
    for j in sorted(all_nodes):
        if not preds[j]:
            L.append(f"    tр({j}) = 0  (исходное событие)")
        else:
            parts = ", ".join(
                f"tр({i})+{t}={early[i]+t}" for i, t in preds[j]
            )
            L.append(f"    tр({j}) = max({parts}) = {early[j]}")

    # 3. Поздние сроки
    hdr("Пункт 3. Поздние сроки свершения событий (обратный проход)")
    L.append("  Формула: tп(i) = min[ tп(j) - t(i,j) ]  для всех j: i → j")
    L.append(f"  Граничное условие: tп({sink}) = tр({sink}) = {early[sink]}")
    L.append("")
    succs = defaultdict(list)
    for i, j, t in edges:
        succs[i].append((j, t))
    for i in sorted(all_nodes, reverse=True):
        if not succs[i]:
            L.append(f"    tп({i}) = {late[i]}  (завершающее событие)")
        else:
            parts = ", ".join(
                f"tп({j})-{t}={late[j]-t}" for j, t in succs[i]
            )
            L.append(f"    tп({i}) = min({parts}) = {late[i]}")

    # 4. Резервы
    hdr("Пункт 4. Резервы времени событий")
    L.append("  Формула: R(j) = tп(j) - tр(j)")
    L.append("")
    for j in sorted(all_nodes):
        cr = "  ← КРИТИЧЕСКОЕ" if reserves[j] == 0 else ""
        L.append(f"    R({j}) = {late[j]} - {early[j]} = {reserves[j]}{cr}")

    # 5. Сводная таблица
    hdr("Пункт 5. Сводная таблица параметров событий")
    hline = f"  +{'─'*6}+{'─'*8}+{'─'*8}+{'─'*8}+{'─'*12}+"
    L.append(hline)
    L.append(f"  | {'№':^4} | {'tр(j)':^6} | {'tп(j)':^6} | "
             f"{'R(j)':^6} | {'Критич.':^10} |")
    L.append(hline)
    for j in sorted(all_nodes):
        cr = "  ДА  " if reserves[j] == 0 else "  нет "
        L.append(f"  | {j:^4} | {early[j]:^6} | {late[j]:^6} | "
                 f"{reserves[j]:^6} | {cr:^10} |")
    L.append(hline)

    # 6. Критический путь
    hdr("Пункт 6. Критический путь")
    L.append("  Критический путь — последовательность событий с R(j) = 0")
    L.append("")
    L.append("  Критические события:")
    L.append("    " + " → ".join(str(e) for e in crit_ev))
    L.append("")
    L.append("  Полный резерв каждой работы:  "
             "Rр(i,j) = tп(j) - tр(i) - t(i,j)")
    L.append("")
    crit_set = {(i, j) for i, j, _ in crit_ed}
    for i, j, t in sorted(edges):
        rf = late[j] - early[i] - t
        cr = "  ← КРИТИЧЕСКАЯ" if (i, j) in crit_set else ""
        L.append(f"    Rр({i},{j}) = tп({j})-tр({i})-t({i},{j}) = "
                 f"{late[j]}-{early[i]}-{t} = {rf}{cr}")
    L.append("")
    L.append("  Критические работы (Rр = 0):")
    if crit_ed:
        for i, j, t in sorted(crit_ed):
            L.append(f"    ({i} → {j}),  t = {t}")
    else:
        L.append("    (нет критических работ)")
    L.append("")
    L.append(f"  Длина критического пути = {early[sink]}")
    L.append(f"  → Минимальное время выполнения всего комплекса работ: "
             f"{early[sink]}")
    L.append("")

    dsep()
    L.append("Все расчёты выполнены.")
    dsep()

    return "\n".join(L)


# ─────────────────────────────────────────────
#  Главная функция
# ─────────────────────────────────────────────

def main():
    print("=" * 72)
    print("  ЛАБОРАТОРНАЯ РАБОТА № 4")
    print("  Оптимизация работ методом сетевого планирования и управления")
    print("=" * 72)

    while True:
        raw = input(
            "\nВведите номер варианта "
            "(0 - пример из методички, 1-16 - ваш вариант): "
        ).strip()
        try:
            choice = int(raw)
            if 0 <= choice <= 16:
                break
            print("  Пожалуйста, введите число от 0 до 16.")
        except ValueError:
            print("  Введите целое число.")

    edges = VARIANTS[choice]

    print(f"\n[!] Загружены данные для варианта {choice}.")
    if choice != 0:
        print("[!] ВНИМАНИЕ: Данные (веса графов) были распознаны с изображений.")
        print("[!] Обязательно сверьте веса (длительности) работ в коде")
        print("[!] с вашей методичкой перед сдачей работы!\n")

    # ── Определяем исходное и завершающее события автоматически ──
    source, sink = find_source_and_sink(edges)
    all_nodes = sorted({v for edge in edges for v in edge[:2]})

    print(f"    Исходное событие:      {source}")
    print(f"    Завершающее событие:   {sink}")
    print(f"    Всего вершин:          {len(all_nodes)}")

    # ── Вычисления ──
    topo   = topological_sort(all_nodes, edges)
    early  = compute_early(all_nodes, edges, topo)
    late   = compute_late(all_nodes, edges, early, topo, sink)
    reserves = compute_reserves(all_nodes, early, late)
    crit_ev, crit_ed = find_critical_path(edges, early, late)

    # ── Отчёт ──
    report = build_report(
        choice, all_nodes, edges,
        early, late, reserves,
        crit_ev, crit_ed,
        source, sink,
    )
    print("\n" + report)

    # ── Сохранение ──
    project_root = Path(__file__).parent.parent.parent
    out_dir = project_root / "output" / "fourthLab"

    out_dir.mkdir(parents=True, exist_ok=True)
    label    = "primer" if choice == 0 else f"N{choice}"
    out_path = out_dir / f"Lab_rabota_4_stud_{label}.txt"

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report + "\n")
    print(f"\n[✓] Результаты сохранены в файл: {out_path}")


if __name__ == "__main__":
    main()