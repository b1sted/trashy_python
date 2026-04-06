"""
Лабораторная работа 3
Принятие решения по оптимизации размещения узла доступа на сети связи района

Решает две задачи:
  1. Минимаксная задача  — нахождение центра графа (для узла радиодоступа)
  2. Минисуммная задача  — нахождение медианы графа (для проводного/кабельного узла)

Топологии графов (рис. 3.2 из методички):
  Граф (а) — нечётные варианты:
      x1─x2, x1─x3, x2─x4, x2─x5, x3─x5, x3─x6, x4─x7, x5─x7, x5─x8, x6─x8, x7─x8
  Граф (б) — чётные варианты:
      x1─x2, x1─x3, x2─x3, x2─x4, x3─x5, x4─x5, x4─x6, x5─x7, x6─x7, x6─x8, x7─x8
"""

import random
import math
from pathlib import Path

# ─────────────────────────────────────────────
#  Исходные данные вариантов (таблица 3.2)
# ─────────────────────────────────────────────
VARIANT_WEIGHTS = {
     1: [70,  60,  60,  70, 130,  40,  60,  80],
     2: [90,  80,  90, 100, 100,  90, 130,  60],
     3: [140, 100,  50,  70, 110,  80, 110, 110],
     4: [50,  70,  90,  50,  70, 140,  80, 110],
     5: [100,  80,  50, 110, 130,  50,  90, 110],
     6: [90, 140, 130, 140,  50,  70,  70,  40],
     7: [60,  80, 120,  90,  40,  80, 110, 120],
     8: [80, 120, 120,  90,  90, 130,  70,  90],
     9: [140,  70,  50, 130,  60,  70,  90,  80],
    10: [90, 100, 110,  70,  50,  60,  80, 100],
    11: [40, 100, 120,  50, 110, 110, 140,  50],
    12: [90,  80,  40, 130,  70, 140,  50, 140],
    13: [100, 110,  90,  40, 100,  60,  90, 110],
    14: [50,  70, 140, 120,  90,  80,  80,  40],
    15: [50, 120,  70,  90, 100, 130, 120,  80],
    16: [140, 110,  60, 110, 120,  40,  50, 130],
    17: [110, 140, 130, 140,  80,  60,  60,  60],
    18: [50,  60, 140, 120,  60,  80,  60,  60],
    19: [50,  40, 140,  90, 130,  60,  60, 140],
    20: [110, 100, 100,  80, 120, 140,  80,  70],
    21: [120,  90,  90,  50, 120,  40,  40,  60],
    22: [60,  80, 100,  80,  90,  40,  80,  40],
    23: [120,  90,  70, 110, 110, 140, 130,  60],
    24: [130,  60,  40, 110, 110,  90, 140, 110],
    25: [80,  80, 100,  60, 140,  70,  80,  60],
    26: [60,  60, 140, 120, 120, 120,  80, 110],
    27: [100, 100,  40, 100, 100, 110, 140,  80],
    28: [120,  70,  50, 140,  60, 120, 100,  60],
    29: [130,  80,  60,  90,  80,  50,  60,  40],
    30: [70,  80,  60,  50,  40,  60,  40,  90],
}

# ─────────────────────────────────────────────
#  Топологии графов (рёбра, индексация с 1)
# ─────────────────────────────────────────────
EDGES_A = [                    # Граф (а) — нечётные варианты
    (1, 2), (1, 3),
    (2, 4), (2, 5),
    (3, 5), (3, 6),
    (4, 7),
    (5, 7), (5, 8),
    (6, 8),
    (7, 8),
]

EDGES_B = [                    # Граф (б) — чётные варианты
    (1, 2), (1, 3),
    (2, 3), (2, 4),
    (3, 5),
    (4, 5), (4, 6),
    (5, 7),
    (6, 7), (6, 8),
    (7, 8),
]

N = 8   # число вершин


# ─────────────────────────────────────────────
#  Алгоритмы
# ─────────────────────────────────────────────

def build_dist_matrix(edges, distances):
    INF = math.inf
    d = [[INF] * (N + 1) for _ in range(N + 1)]
    for i in range(1, N + 1):
        d[i][i] = 0
    for u, v in edges:
        w = distances[(u, v)]
        d[u][v] = w
        d[v][u] = w
    return d


def floyd_warshall(d):
    dist = [row[:] for row in d]
    for k in range(1, N + 1):
        for i in range(1, N + 1):
            for j in range(1, N + 1):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    return dist


def solve_minimax(dist):
    best_vertex, best_val = -1, math.inf
    row_maxes = []
    for i in range(1, N + 1):
        mx = max(dist[i][j] for j in range(1, N + 1) if j != i)
        row_maxes.append(mx)
        if mx < best_val:
            best_val = mx
            best_vertex = i
    return best_vertex, best_val, row_maxes


def solve_minisum(dist, weights):
    best_vertex, best_val = -1, math.inf
    fi_values = []
    for i in range(1, N + 1):
        fi = sum(dist[i][j] * weights[j - 1] for j in range(1, N + 1) if j != i)
        fi_values.append(fi)
        if fi < best_val:
            best_val = fi
            best_vertex = i
    return best_vertex, best_val, fi_values


# ─────────────────────────────────────────────
#  Ввод расстояний
# ─────────────────────────────────────────────

def input_distances(edges):
    print("\nРасстояния между населёнными пунктами (допустимый диапазон: 3–15 км).")
    print("Нажмите Enter без ввода, чтобы сгенерировать случайное значение.\n")
    distances = {}
    for u, v in edges:
        while True:
            raw = input(f"  Расстояние x{u}─x{v} (км): ").strip()
            if raw == "":
                val = random.randint(3, 15)
                print(f"    -> сгенерировано: {val} км")
                distances[(u, v)] = val
                break
            try:
                val = int(raw)
                if 3 <= val <= 15:
                    distances[(u, v)] = val
                    break
                else:
                    print("    Значение должно быть от 3 до 15 км. Повторите ввод.")
            except ValueError:
                print("    Введите целое число. Повторите ввод.")
    return distances


def auto_distances(edges):
    return {(u, v): random.randint(3, 15) for u, v in edges}


# ─────────────────────────────────────────────
#  Построение отчёта
# ─────────────────────────────────────────────

def build_report(variant, weights, edges, graph_type, distances, dist,
                 center, center_val, row_maxes,
                 median, median_val, fi_values):
    W = 70
    L = []

    def sep():  L.append("-" * W)
    def dsep(): L.append("=" * W)
    def hdr(t):
        L.append("")
        sep()
        L.append(t)
        sep()
        L.append("")

    # -- Шапка --
    dsep()
    L.append(f"{'Лабораторная работа 3':^{W}}")
    L.append(f"{'Оптимизация размещения узла доступа на сети связи района':^{W}}")
    dsep()

    # -- 1. Исходные данные --
    hdr("Пункт 1. Исходные данные варианта")
    L.append(f"  Вариант № {variant}  |  Граф {graph_type}  |  Вершин: {N}")
    L.append("")
    L.append("  Количество абонентов в населённых пунктах (веса вершин):")
    L.append("")
    for i, w in enumerate(weights, 1):
        L.append(f"    x{i}: {w} абонентов")
    L.append("")
    L.append("  Ребра графа и расстояния (км):")
    L.append("")
    for (u, v), d in distances.items():
        L.append(f"    x{u}-x{v}: {d} км")

    # -- 2. Матрица кратчайших расстояний --
    hdr("Пункт 2. Матрица кратчайших расстояний d_ij (алгоритм Флойда-Уоршелла)")
    col_hdr = "       " + "".join(f"  x{j:<4}" for j in range(1, N + 1)) + "   max"
    L.append(col_hdr)
    sep()
    for i in range(1, N + 1):
        row = f"  x{i}   "
        for j in range(1, N + 1):
            val = dist[i][j]
            row += "   inf " if val == math.inf else f"  {val:<5.0f}"
        row += f"  {row_maxes[i - 1]:<5.0f}"
        marker = "  <- min(max)" if i == center else ""
        L.append(row + marker)
    sep()

    # -- 3. Минимаксная задача --
    hdr("Пункт 3. Минимаксная задача — центр графа (узел радиодоступа)")
    L.append("  Критерий оптимальности:")
    L.append("    Fi = max(d_ij)  ->  min")
    L.append("         j≠i")
    L.append("")
    L.append("  Максимальные расстояния из каждой вершины:")
    L.append("")
    for i, mx in enumerate(row_maxes, 1):
        marker = "  <- МИНИМУМ" if i == center else ""
        L.append(f"    x{i}: max(d_ij) = {mx:.0f} км{marker}")
    L.append("")
    L.append(f"  Центр графа: вершина x{center}")
    L.append(f"  Критерий:    min[max(d_ij)] = {center_val:.0f} км")
    L.append("")
    L.append(f"  -> Узел радиодоступа размещается в населённом пункте x{center}")

    # -- 4. Минисуммная задача --
    hdr("Пункт 4. Минисуммная задача — медиана графа (кабельный узел доступа)")
    L.append("  Критерий оптимальности:")
    L.append("    Fi = SUM d_ij * p_j  ->  min")
    L.append("         j≠i")
    L.append("")
    L.append("  Значения взвешенной целевой функции F_i:")
    L.append("")
    for i, fi in enumerate(fi_values, 1):
        marker = "  <- МИНИМУМ" if i == median else ""
        L.append(f"    F{i} = {fi:.0f}{marker}")
    L.append("")
    L.append(f"  Медиана графа: вершина x{median}")
    L.append(f"  Критерий:      F_min = {median_val:.0f}")
    L.append("")
    L.append(f"  -> Кабельный узел доступа размещается в населённом пункте x{median}")

    # -- 5. Итоговые результаты --
    hdr("Пункт 5. Итоговые результаты")
    L.append("  Задача 1 (радиодоступ — МИНИМАКСНАЯ задача):")
    L.append(f"    Центр графа:  x{center}")
    L.append(f"    max(d_ij)  =  {center_val:.0f} км")
    L.append(f"    Вывод: узел радиодоступа размещается в пункте x{center},")
    L.append(f"           максимальное расстояние до абонентов не превысит {center_val:.0f} км.")
    L.append("")
    L.append("  Задача 2 (проводной/кабельный доступ — МИНИСУММНАЯ задача):")
    L.append(f"    Медиана графа: x{median}")
    L.append(f"    F_min        = {median_val:.0f}")
    L.append(f"    Вывод: кабельный узел доступа размещается в пункте x{median},")
    L.append(f"           суммарная взвешенная длина кабельных трасс минимальна.")
    L.append("")

    project_root = Path(__file__).parent.parent.parent
    out_dir = project_root / "output" / "thirdLab"

    dsep()
    L.append(f"Файл с результатами: {out_dir / f'Lab_rabota_3_stud_N{variant}.txt'}")
    L.append("Все расчёты выполнены.")
    dsep()

    return "\n".join(L)


# ─────────────────────────────────────────────
#  Главная функция
# ─────────────────────────────────────────────

def main():
    print("=" * 70)
    print("  ЛАБОРАТОРНАЯ РАБОТА № 3")
    print("  Оптимизация размещения узла доступа на сети связи района")
    print("=" * 70)

    # 1. Выбор варианта
    while True:
        try:
            variant = int(input("\nВведите номер варианта (1–30): ").strip())
            if 1 <= variant <= 30:
                break
            print("  Вариант должен быть от 1 до 30.")
        except ValueError:
            print("  Введите целое число.")

    weights    = VARIANT_WEIGHTS[variant]
    edges      = EDGES_A if variant % 2 == 1 else EDGES_B
    graph_type = "(а) — нечётный" if variant % 2 == 1 else "(б) — чётный"

    # 2. Ввод расстояний
    print("\nКак задать расстояния?")
    print("  1 — Ввести вручную")
    print("  2 — Сгенерировать случайно (3–15 км)")
    while True:
        choice = input("Ваш выбор (1/2): ").strip()
        if choice in ("1", "2"):
            break
        print("  Введите 1 или 2.")

    if choice == "1":
        distances = input_distances(edges)
    else:
        distances = auto_distances(edges)
        print("\n  Сгенерированные расстояния:")
        for (u, v), d in distances.items():
            print(f"    x{u}-x{v}: {d} км")

    # 3. Вычисления
    d0                              = build_dist_matrix(edges, distances)
    dist                            = floyd_warshall(d0)
    center, center_val, row_maxes   = solve_minimax(dist)
    median, median_val, fi_values   = solve_minisum(dist, weights)

    # 4. Формируем отчёт и печатаем
    report = build_report(
        variant, weights, edges, graph_type, distances, dist,
        center, center_val, row_maxes,
        median, median_val, fi_values,
    )
    print("\n" + report)

    # 5. Сохраняем в файл автоматически
    project_root = Path(__file__).parent.parent.parent
    out_dir = project_root / "output" / "thirdLab"

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"Lab_rabota_3_stud_N{variant}.txt"

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report + "\n")
    print(f"\n  Результаты сохранены в файл: {out_path}")


if __name__ == "__main__":
    main()