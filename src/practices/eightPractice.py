"""
Практическая работа 8 — Решение технологической задачи
Три экскаватора роют котлован объёмом a м³ при запасе топлива c л.
  Мощный:  22.5 м³/ч,  10 л/ч
  Средний: 10   м³/ч,   b л/ч
  Малый:    5   м³/ч,   2 л/ч

Переменные x1, x2, x3 — часы работы каждого экскаватора.

Задание 1: минимизировать время выполнения работы T
Задание 2: минимизировать расход топлива при выполнении работы
"""

import os
import sys
from fractions import Fraction
from itertools import combinations
from scipy.optimize import linprog

# ─── Таблица вариантов ────────────────────────────────────────────────────────
VARIANTS = {
    1:  {"a": 1350, "b": Fraction(10, 3), "c": 548},
    2:  {"a": 1080, "b": Fraction(4),     "c": 460},
    3:  {"a": 1080, "b": Fraction(11, 3), "c": 444},
    4:  {"a": 1440, "b": Fraction(10, 3), "c": 580},
    5:  {"a": 1140, "b": Fraction(4),     "c": 480},
    6:  {"a": 1350, "b": Fraction(11, 3), "c": 552},
    7:  {"a": 1620, "b": Fraction(10, 3), "c": 656},
    8:  {"a": 2160, "b": Fraction(11, 3), "c": 888},
    9:  {"a": 1200, "b": Fraction(4),     "c": 500},
    10: {"a": 1320, "b": Fraction(4),     "c": 550},
    11: {"a": 1890, "b": Fraction(11, 3), "c": 777},
    12: {"a": 1200, "b": Fraction(4),     "c": 510},
    13: {"a": 1800, "b": Fraction(10, 3), "c": 728},
    14: {"a": 1380, "b": Fraction(4),     "c": 580},
    15: {"a": 1620, "b": Fraction(11, 3), "c": 666},
}

# ─── Все 7 непустых подмножеств {0=мощный, 1=средний, 2=малый} ───────────────
ALL_SUBSETS = []
SUBSET_NAMES = []
for r in range(1, 4):
    for combo in combinations([0, 1, 2], r):
        ALL_SUBSETS.append(list(combo))
        labels = {0: "x1(мощный)", 1: "x2(средний)", 2: "x3(малый)"}
        SUBSET_NAMES.append(" + ".join(labels[i] for i in combo))

# ─── Выбор варианта ───────────────────────────────────────────────────────────
try:
    VARIANT_NUMBER = int(input("Введите номер варианта (1–15): "))
except ValueError:
    print("Ошибка: введите целое число.")
    sys.exit(1)

if VARIANT_NUMBER not in VARIANTS:
    print(f"Вариант {VARIANT_NUMBER} не существует. Доступны: 1–15.")
    sys.exit(1)

# ─── Вывод (консоль + файл) ───────────────────────────────────────────────────
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "output", "eightPractice")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, f"Practice_8_N{VARIANT_NUMBER}.txt")

lines = []

def out(text=""):
    print(text)
    lines.append(text)

# ─── Параметры варианта ───────────────────────────────────────────────────────
params = VARIANTS[VARIANT_NUMBER]
a = params["a"]
b = float(params["b"])
c = params["c"]
b_frac = params["b"]

# ─── Шапка ───────────────────────────────────────────────────────────────────
print()
out("=" * 70)
out("  Практическая работа 8 — Решение технологической задачи")
out(f"  Вариант {VARIANT_NUMBER}")
out("=" * 70)
out()
out("Исходные данные:")
out(f"  a = {a} м³   (объём котлована)")
out(f"  b = {b_frac} л/ч  (расход топлива среднего экскаватора)")
out(f"  c = {c} л    (запас топлива)")
out()
out("Экскаваторы:")
out("  Мощный  (x1): производительность 22.5 м³/ч, расход 10  л/ч")
out(f"  Средний (x2): производительность 10   м³/ч, расход {b_frac} л/ч")
out("  Малый   (x3): производительность  5   м³/ч, расход  2  л/ч")
out()

# ─── Общая постановка ────────────────────────────────────────────────────────
out("─" * 70)
out("ПОСТАНОВКА ЗАДАЧИ")
out("─" * 70)
out()
out("Переменные:")
out("  x1 (ч) — время работы мощного экскаватора")
out("  x2 (ч) — время работы среднего экскаватора")
out("  x3 (ч) — время работы малого экскаватора")
out()
out("Общие ограничения (для обоих заданий):")
out(f"  22.5·x1 + 10·x2 + 5·x3 ≥ {a}   (выполнение объёма котлована)")
out(f"  10·x1 + {b_frac}·x2 + 2·x3 ≤ {c}        (не превысить запас топлива)")
out("  x1, x2, x3 ≥ 0")
out()
out("Рассматриваются все 7 непустых подмножеств {x1, x2, x3}.")
out("Если экскаватор не входит в конфигурацию — его время равно 0.")
out()

# ─── Постановка задания 1 ─────────────────────────────────────────────────────
out("─" * 70)
out("ЗАДАНИЕ 1 — Постановка задачи линейного программирования")
out("─" * 70)
out()
out("Цель: выполнить работу как можно скорее.")
out()
out("Поскольку экскаваторы работают одновременно, продолжительность работ")
out("  T = max{x1, x2, x3}.")
out("Функция max нелинейна, однако она линеаризуется стандартным приёмом:")
out("  вводится вспомогательная переменная T ≥ 0 и добавляются ограничения")
out("  xi ≤ T для каждого i. Тогда T автоматически принимает значение max{xi}.")
out("Задача остаётся задачей линейного программирования.")
out()
out("  Переменные: T, x1, x2, x3")
out()
out("  Целевая функция (линейная по всем переменным):")
out("    1·T + 0·x1 + 0·x2 + 0·x3  →  min")
out()
out("  Система ограничений:")
out(f"    (1)  0·T + 22.5·x1 + 10·x2 +  5·x3  ≥ {a}   [объём]")
out(f"    (2)  0·T +   10·x1 + {b_frac}·x2 +  2·x3  ≤ {c}    [топливо]")
out(  "    (3) -1·T +    1·x1 +  0·x2 +  0·x3  ≤ 0    [x1 ≤ T]")
out(  "    (4) -1·T +    0·x1 +  1·x2 +  0·x3  ≤ 0    [x2 ≤ T]")
out(  "    (5) -1·T +    0·x1 +  0·x2 +  1·x3  ≤ 0    [x3 ≤ T]")
out(  "    (6)  T ≥ 0,  x1 ≥ 0,  x2 ≥ 0,  x3 ≥ 0")
out()

# ─── Постановка задания 2 ─────────────────────────────────────────────────────
out("─" * 70)
out("ЗАДАНИЕ 2 — Постановка задачи линейного программирования")
out("─" * 70)
out()
out("Цель: выполнить работу при максимальной экономии топлива.")
out()
out("  Переменные: x1, x2, x3")
out()
out("  Целевая функция (линейная по всем переменным):")
out(f"    10·x1 + {b_frac}·x2 + 2·x3  →  min")
out()
out("  Система ограничений:")
out(f"    (1)  22.5·x1 + 10·x2 + 5·x3  ≥ {a}   [объём]")
out(f"    (2)   10·x1 + {b_frac}·x2 + 2·x3  ≤ {c}    [топливо]")
out(  "    (3)  x1 ≥ 0,  x2 ≥ 0,  x3 ≥ 0")
out()


# ══════════════════════════════════════════════════════════════════════════════
# Вспомогательные функции
# ══════════════════════════════════════════════════════════════════════════════

def fmt_x(v):
    """Обнуляет малые/отрицательные значения (артефакты солвера), исключает -0.0."""
    return 0.0 if v < 1e-9 else v


def solve_task1(subset, a, b, c):
    """
    Задание 1: min 1·T + 0·x1 + 0·x2 + 0·x3
    Переменные: [T, x1, x2, x3]
    """
    A_ub = [
        [0, -22.5, -10,  -5],   # (1) объём: -22.5x1-10x2-5x3 ≤ -a
        [0,  10,    b,    2],   # (2) топливо
        [-1,  1,    0,    0],   # (3) x1 - T ≤ 0
        [-1,  0,    1,    0],   # (4) x2 - T ≤ 0
        [-1,  0,    0,    1],   # (5) x3 - T ≤ 0
    ]
    b_ub = [-a, c, 0, 0, 0]

    # Фиксируем xi = 0 для экскаваторов вне подмножества
    for i in range(3):
        if i not in subset:
            row = [0, 0, 0, 0]
            row[i + 1] = 1
            A_ub.append(row)
            b_ub.append(0)

    res = linprog(
        [1, 0, 0, 0],          # целевая функция: 1·T + 0·x1 + 0·x2 + 0·x3
        A_ub=A_ub, b_ub=b_ub,
        bounds=[(0, None)] * 4,
        method="highs"
    )

    if not res.success:
        return None

    T_opt  = fmt_x(res.x[0])
    x1_opt = fmt_x(res.x[1])
    x2_opt = fmt_x(res.x[2])
    x3_opt = fmt_x(res.x[3])
    fuel   = 10 * x1_opt + b * x2_opt + 2 * x3_opt
    vol    = 22.5 * x1_opt + 10 * x2_opt + 5 * x3_opt
    return {"T": T_opt, "x1": x1_opt, "x2": x2_opt, "x3": x3_opt,
            "fuel": fuel, "vol": vol}


def solve_task2(subset, a, b, c):
    """
    Задание 2: min 10·x1 + b·x2 + 2·x3
    Переменные: [x1, x2, x3]
    """
    A_ub = [
        [-22.5, -10,  -5],   # объём
        [ 10,    b,    2],   # топливо
    ]
    b_ub = [-a, c]

    for i in range(3):
        if i not in subset:
            row = [0, 0, 0]
            row[i] = 1
            A_ub.append(row)
            b_ub.append(0)

    res = linprog(
        [10, b, 2],
        A_ub=A_ub, b_ub=b_ub,
        bounds=[(0, None)] * 3,
        method="highs"
    )

    if not res.success:
        return None

    x1_opt = fmt_x(res.x[0])
    x2_opt = fmt_x(res.x[1])
    x3_opt = fmt_x(res.x[2])
    fuel   = 10 * x1_opt + b * x2_opt + 2 * x3_opt
    vol    = 22.5 * x1_opt + 10 * x2_opt + 5 * x3_opt
    T_val  = max(x1_opt, x2_opt, x3_opt)
    return {"fuel": fuel, "x1": x1_opt, "x2": x2_opt, "x3": x3_opt,
            "T": T_val, "vol": vol}


# ══════════════════════════════════════════════════════════════════════════════
# ЗАДАНИЕ 1 — перебор подмножеств
# ══════════════════════════════════════════════════════════════════════════════
out("─" * 70)
out("ЗАДАНИЕ 1 — Результаты решения по всем конфигурациям")
out("─" * 70)
out()
out("Целевая функция:  1·T + 0·x1 + 0·x2 + 0·x3  →  min")
out("(T — продолжительность работ; xi ≤ T обеспечивают T = max{xi})")
out()

results1 = []
for subset, name in zip(ALL_SUBSETS, SUBSET_NAMES):
    r = solve_task1(subset, a, b, c)
    results1.append((name, subset, r))

valid1 = [(name, r) for name, _, r in results1 if r is not None]
best1   = min(valid1, key=lambda x: x[1]["T"]) if valid1 else None
best_T  = best1[1]["T"] if best1 else None

header = f"  {'Конфигурация':<26} {'T (ч)':>10} {'x1 (ч)':>10} {'x2 (ч)':>10} {'x3 (ч)':>10} {'Топливо (л)':>12}"
out(header)
out("  " + "-" * 80)

for name, subset, r in results1:
    if r is None:
        prod_vals = [22.5, 10, 5]
        fuel_vals = [10, b, 2]
        p_s = sum(prod_vals[i] for i in subset)
        f_s = sum(fuel_vals[i] for i in subset)
        need_t = a / p_s
        max_t  = c / f_s
        reason = f"T≥{need_t:.1f} (объём), T≤{max_t:.1f} (топливо) — противоречие"
        out(f"    {name:<25}  {'нет решения':>10}   ({reason})")
    else:
        star = "★" if best_T is not None and abs(r["T"] - best_T) < 0.01 else " "
        out(f"  {star} {name:<25} {r['T']:>10.4f} {r['x1']:>10.4f} {r['x2']:>10.4f} {r['x3']:>10.4f} {r['fuel']:>12.4f}")

out()
if best1:
    r1 = best1[1]
    out(f"  ★ Оптимальная конфигурация: {best1[0]}")
    out(f"    Значение целевой функции (T): {r1['T']:.4f} ч  ({r1['T']*60:.1f} мин)")
    out(f"    x1 = {r1['x1']:.4f} ч,  x2 = {r1['x2']:.4f} ч,  x3 = {r1['x3']:.4f} ч")
    fuel_comment = ('используется полностью'
                    if abs(r1['fuel'] - c) < 0.1
                    else f"остаток {c - r1['fuel']:.2f} л")
    out(f"    Расход топлива = {r1['fuel']:.4f} л  (запас {c} л, {fuel_comment})")
    out(f"    Объём выполнен: {r1['vol']:.2f} м³  (требуется ≥ {a} м³)")
out()


# ══════════════════════════════════════════════════════════════════════════════
# ЗАДАНИЕ 2 — перебор подмножеств
# ══════════════════════════════════════════════════════════════════════════════
out("─" * 70)
out("ЗАДАНИЕ 2 — Результаты решения по всем конфигурациям")
out("─" * 70)
out()
out(f"Целевая функция:  10·x1 + {b_frac}·x2 + 2·x3  →  min")
out()

results2 = []
for subset, name in zip(ALL_SUBSETS, SUBSET_NAMES):
    r = solve_task2(subset, a, b, c)
    results2.append((name, subset, r))

valid2     = [(name, r) for name, _, r in results2 if r is not None]
best2      = min(valid2, key=lambda x: x[1]["fuel"]) if valid2 else None
best_fuel  = best2[1]["fuel"] if best2 else None

header2 = f"  {'Конфигурация':<26} {'Топливо (л)':>12} {'x1 (ч)':>10} {'x2 (ч)':>10} {'x3 (ч)':>10} {'Время (ч)':>10}"
out(header2)
out("  " + "-" * 80)

for name, subset, r in results2:
    if r is None:
        prod_vals = [22.5, 10, 5]
        fuel_vals = [10, b, 2]
        p_s = sum(prod_vals[i] for i in subset)
        f_s = sum(fuel_vals[i] for i in subset)
        need_t = a / p_s
        max_t  = c / f_s
        reason = f"T≥{need_t:.1f} (объём), T≤{max_t:.1f} (топливо) — противоречие"
        out(f"    {name:<25}  {'нет решения':>12}   ({reason})")
    else:
        star = "★" if best_fuel is not None and abs(r["fuel"] - best_fuel) < 0.01 else " "
        out(f"  {star} {name:<25} {r['fuel']:>12.4f} {r['x1']:>10.4f} {r['x2']:>10.4f} {r['x3']:>10.4f} {r['T']:>10.4f}")

out()
if best2:
    r2 = best2[1]
    out(f"  ★ Оптимальная конфигурация: {best2[0]}")
    out(f"    Значение целевой функции (топливо): {r2['fuel']:.4f} л")
    out(f"    x1 = {r2['x1']:.4f} ч,  x2 = {r2['x2']:.4f} ч,  x3 = {r2['x3']:.4f} ч")
    out(f"    Экономия топлива: {c - r2['fuel']:.2f} л  (запас {c} л)")
    out(f"    Время работ (по max xi): {r2['T']:.4f} ч  ({r2['T']*60:.1f} мин)")
    out(f"    Объём выполнен: {r2['vol']:.2f} м³  (требуется ≥ {a} м³)")
out()


# ─── Итог ─────────────────────────────────────────────────────────────────────
out("=" * 70)
out("ИТОГ")
out("=" * 70)
if best1:
    out(f"  Задание 1  (min T):         T*  = {best1[1]['T']:.4f} ч"
        f"  | {best1[0]}"
        f"  | топливо = {best1[1]['fuel']:.2f} л")
if best2:
    out(f"  Задание 2  (min топливо):   Q*  = {best2[1]['fuel']:.4f} л"
        f"  | {best2[0]}"
        f"  | время ≈ {best2[1]['T']:.4f} ч")
out()

# ─── Запись в файл ────────────────────────────────────────────────────────────
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print(f"\n[Файл сохранён: {OUTPUT_FILE}]")