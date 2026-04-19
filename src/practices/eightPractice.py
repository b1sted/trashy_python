"""
Практическая работа 8 — Решение технологической задачи
Три экскаватора роют котлован объёмом a м³ при запасе топлива c л.
  Мощный:  22.5 м³/ч,  10 л/ч
  Средний: 10   м³/ч,   b л/ч
  Малый:    5   м³/ч,   2 л/ч

Переменные x1, x2, x3 — часы работы каждого экскаватора.

Задание 1: минимизировать время выполнения работы T
Задание 2: минимизировать расход топлива при выполнении работы

Рассматриваются все 7 непустых подмножеств {x1, x2, x3}.
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
    """Печатает строку в консоль и сохраняет для файла."""
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

# ─── Постановка задачи ────────────────────────────────────────────────────────
out("─" * 70)
out("ПОСТАНОВКА ЗАДАЧИ")
out("─" * 70)
out()
out("Переменные:")
out("  x1, x2, x3 — часы работы мощного, среднего и малого")
out("               экскаваторов соответственно.")
out()
out("Ограничения (общие для обоих заданий):")
out(f"  (1) 22.5·x1 + 10·x2 + 5·x3 >= {a}   (объём должен быть выполнен)")
out(f"  (2) 10·x1 + {b_frac}·x2 + 2·x3 <= {c}       (не превысить запас топлива)")
out("  (3) x1, x2, x3 >= 0")
out()
out("Рассматриваются все 7 непустых подмножеств {x1, x2, x3}.")
out("Если экскаватор не входит в конфигурацию — его время принудительно = 0.")
out()


# ═══════════════════════════════════════════════════════════════════════════════
# Вспомогательная функция: решить задачу для одного подмножества
# ═══════════════════════════════════════════════════════════════════════════════

def fmt_x(v):
    """Обнуляет малые отрицательные значения (артефакты солвера)."""
    return max(v, 0.0)


def solve_task1(subset, a, b, c):
    """
    Задание 1: min T, переменные [T, x1, x2, x3].
    Для экскаваторов вне subset добавляем xi = 0.
    """
    A_ub = [
        [0, -22.5, -10,  -5],   # объём >= a  →  -объём <= -a
        [0,  10,    b,    2],   # топливо <= c
        [-1,  1,    0,    0],   # x1 - T <= 0
        [-1,  0,    1,    0],   # x2 - T <= 0
        [-1,  0,    0,    1],   # x3 - T <= 0
    ]
    b_ub = [-a, c, 0, 0, 0]

    for i in range(3):
        if i not in subset:
            row = [0, 0, 0, 0]
            row[i + 1] = 1
            A_ub.append(row)
            b_ub.append(0)

    res = linprog(
        [1, 0, 0, 0],
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
    Задание 2: min (10·x1 + b·x2 + 2·x3), переменные [x1, x2, x3].
    Для экскаваторов вне subset добавляем xi = 0.
    """
    A_ub = [
        [-22.5, -10,  -5],   # объём >= a
        [ 10,    b,    2],   # топливо <= c
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


# ═══════════════════════════════════════════════════════════════════════════════
# ЗАДАНИЕ 1 — минимизировать время T
# ═══════════════════════════════════════════════════════════════════════════════
out("─" * 70)
out("ЗАДАНИЕ 1 — Выполнить работу как можно скорее")
out("─" * 70)
out()
out("Целевая функция:  T → min   (T — продолжительность работ в часах)")
out("Доп. ограничения: xi ≤ T  для каждого экскаватора i")
out()

results1 = []
for subset, name in zip(ALL_SUBSETS, SUBSET_NAMES):
    r = solve_task1(subset, a, b, c)
    results1.append((name, subset, r))

# Найти оптимум
valid1 = [(name, r) for name, _, r in results1 if r is not None]
if valid1:
    best1 = min(valid1, key=lambda x: x[1]["T"])
    best_T = best1[1]["T"]
else:
    best_T = None

# Вывод таблицы задания 1
header = f"  {'Конфигурация':<26} {'T (ч)':>10} {'x1 (ч)':>10} {'x2 (ч)':>10} {'x3 (ч)':>10} {'Топливо (л)':>12}"
out(header)
out("  " + "-" * 80)

for name, subset, r in results1:
    if r is None:
        # Пояснение почему нет решения
        x_max_vol = a / sum([22.5, 10, 5][i] for i in subset)
        x_max_fuel = c / sum([10, b, 2][i] for i in subset)
        reason = f"объём требует x>={x_max_vol:.1f}, топливо ограничивает x<={x_max_fuel:.1f}"
        out(f"  {'':1} {name:<25} {'нет решения':>10}   ({reason})")
    else:
        star = "★" if abs(r["T"] - best_T) < 0.01 else " "
        x1s = abs(max(r['x1'], 0.0))
        x2s = abs(max(r['x2'], 0.0))
        x3s = abs(max(r['x3'], 0.0))
        out(f"  {star} {name:<25} {r['T']:>10.4f} {x1s:>10.4f} {x2s:>10.4f} {x3s:>10.4f} {r['fuel']:>12.4f}")

out()
if best_T is not None:
    out(f"  ★ Оптимальная конфигурация: {best1[0]}")
    out(f"    Минимальное время T = {best1[1]['T']:.4f} ч  ({best1[1]['T']*60:.1f} мин)")
    out(f"    Топливо = {best1[1]['fuel']:.4f} л  (запас {c} л, {'используется полностью' if abs(best1[1]['fuel']-c)<0.1 else 'остаток ' + str(round(c-best1[1]['fuel'],2)) + ' л'})")
    out(f"    Объём выполнен: {best1[1]['vol']:.2f} м³  (требуется >= {a})")
out()


# ═══════════════════════════════════════════════════════════════════════════════
# ЗАДАНИЕ 2 — минимизировать расход топлива
# ═══════════════════════════════════════════════════════════════════════════════
out("─" * 70)
out("ЗАДАНИЕ 2 — Максимальная экономия топлива")
out("─" * 70)
out()
out(f"Целевая функция:  10·x1 + {b_frac}·x2 + 2·x3 → min")
out()

results2 = []
for subset, name in zip(ALL_SUBSETS, SUBSET_NAMES):
    r = solve_task2(subset, a, b, c)
    results2.append((name, subset, r))

valid2 = [(name, r) for name, _, r in results2 if r is not None]
if valid2:
    best2 = min(valid2, key=lambda x: x[1]["fuel"])
    best_fuel = best2[1]["fuel"]
else:
    best_fuel = None

header2 = f"  {'Конфигурация':<26} {'Топливо (л)':>12} {'x1 (ч)':>10} {'x2 (ч)':>10} {'x3 (ч)':>10} {'Время (ч)':>10}"
out(header2)
out("  " + "-" * 80)

for name, subset, r in results2:
    if r is None:
        x_max_vol = a / sum([22.5, 10, 5][i] for i in subset)
        x_max_fuel = c / sum([10, b, 2][i] for i in subset)
        reason = f"объём требует x>={x_max_vol:.1f}, топливо ограничивает x<={x_max_fuel:.1f}"
        out(f"  {'':1} {name:<25} {'нет решения':>12}   ({reason})")
    else:
        star = "★" if abs(r["fuel"] - best_fuel) < 0.01 else " "
        x1s = abs(max(r['x1'], 0.0))
        x2s = abs(max(r['x2'], 0.0))
        x3s = abs(max(r['x3'], 0.0))
        out(f"  {star} {name:<25} {r['fuel']:>12.4f} {x1s:>10.4f} {x2s:>10.4f} {x3s:>10.4f} {r['T']:>10.4f}")

out()
if best_fuel is not None:
    out(f"  ★ Оптимальная конфигурация: {best2[0]}")
    out(f"    Минимальный расход топлива = {best2[1]['fuel']:.4f} л  (запас {c} л, экономия {c - best2[1]['fuel']:.2f} л)")
    out(f"    Время (по max xi) = {best2[1]['T']:.4f} ч  ({best2[1]['T']*60:.1f} мин)")
    out(f"    Объём выполнен: {best2[1]['vol']:.2f} м³  (требуется >= {a})")
out()


# ─── Итог ─────────────────────────────────────────────────────────────────────
out("=" * 70)
out("ИТОГ")
out("=" * 70)
if best_T is not None:
    out(f"  Задание 1 (мин. время):   T = {best1[1]['T']:.4f} ч  "
        f"| конфигурация: {best1[0]}  | топливо = {best1[1]['fuel']:.2f} л")
if best_fuel is not None:
    out(f"  Задание 2 (мин. топливо): топливо = {best2[1]['fuel']:.4f} л  "
        f"| конфигурация: {best2[0]}  | время ≈ {best2[1]['T']:.4f} ч")
out()

# ─── Запись в файл ────────────────────────────────────────────────────────────
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print(f"\n[Файл сохранён: {OUTPUT_FILE}]")
