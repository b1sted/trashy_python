"""
Лабораторная работа №2 — Вариант №16
Симплекс-метод. Прямая и двойственная задача.
"""

import numpy as np
from scipy.optimize import linprog, milp, LinearConstraint, Bounds
from pathlib import Path

PRODUCTS  = ["Q1", "Q2"]
RESOURCES = ["S1", "S2", "S3"]
PROFIT    = np.array([3.0, 2.0])
A         = np.array([[3., 1.],
                       [2., 2.],
                       [0., 3.]])
B         = np.array([21., 30., 16.])


def solve_lp(c, A_ub, b_ub, integer=False):
    if integer:
        res = milp(-c,
                   constraints=LinearConstraint(A_ub, -np.inf, b_ub),
                   integrality=np.ones(len(c)),
                   bounds=Bounds(lb=0))
    else:
        res = linprog(-c, A_ub=A_ub, b_ub=b_ub,
                      bounds=[(0, None)] * len(c), method='highs')
    if not res.success:
        raise RuntimeError(res.message)
    return res.x, -res.fun


def solve_dual(A, b, c):
    res = linprog(b, A_ub=-A.T, b_ub=-c,
                  bounds=[(0, None)] * len(b), method='highs')
    if not res.success:
        raise RuntimeError(res.message)
    return res.x, res.fun


x_cont, F_cont = solve_lp(PROFIT, A, B, integer=False)
x_int,  F_int  = solve_lp(PROFIT, A, B, integer=True)
y,      Z_min  = solve_dual(A, B, PROFIT)
slack_cont     = B - A @ x_cont
slack_int      = B - A @ x_int
duality_ok     = abs(F_cont - Z_min) < 1e-6


def build_report():
    L = []
    W = 70

    def sep():  L.append("─" * W)
    def dsep(): L.append("=" * W)
    def hdr(t):
        L.append("")
        sep()
        L.append(t)
        sep()
        L.append("")

    dsep()
    L.append(f"{'Лабораторная работа 2. Вариант 16':^{W}}")
    dsep()

    # ── 1. Постановка ─────────────────────────────────────────────
    hdr("Пункт 1. Постановка прямой задачи")
    L.append("Условие задачи:")
    L.append("  Предприятие располагает запасами сырья S1, S2, S3.")
    L.append("  Из сырья изготавливается 2 вида изделий Q1 и Q2.")
    L.append("")
    L.append(f"  {'Сырьё':<6}  {'Запас':>6}    {'Q1':>6}    {'Q2':>6}")
    sep()
    for ri, bi, a0, a1 in zip(RESOURCES, B, A[:,0], A[:,1]):
        L.append(f"  {ri:<6}  {bi:>6.0f}    {a0:>6.0f}    {a1:>6.0f}")
    sep()
    L.append(f"  {'Прибыль':<6}              {PROFIT[0]:>6.0f}    {PROFIT[1]:>6.0f}")
    L.append("")
    L.append("Математическая модель:")
    L.append("")
    L.append("  F = 3*x1 + 2*x2  -->  max")
    L.append("")
    L.append("  Ограничения:")
    L.append("    3*x1 + 1*x2 <= 21   (S1)")
    L.append("    2*x1 + 2*x2 <= 30   (S2)")
    L.append("    0*x1 + 3*x2 <= 16   (S3)")
    L.append("    x1, x2 >= 0")

    # ── 2. Непрерывная задача ─────────────────────────────────────
    hdr("Пункт 2. Решение прямой задачи (непрерывный план)")
    L.append("Метод: симплекс-метод (scipy.optimize.linprog, метод HiGHS)")
    L.append("")
    for p, xi in zip(PRODUCTS, x_cont):
        L.append(f"  {p} = {xi:.6f} ед.")
    L.append("")
    L.append(f"  F_max = {F_cont:.6f} д.е.")
    L.append("")
    L.append("Загрузка ресурсов:")
    for ri, used, sl, bi in zip(RESOURCES, A @ x_cont, slack_cont, B):
        status = "ДЕФИЦИТНЫЙ (использован полностью)" if abs(sl) < 1e-6 \
                 else f"остаток = {sl:.4f}"
        L.append(f"  {ri}: использовано {used:.4f} из {bi:.0f}  [{status}]")
    L.append("")
    L.append("Проверка выполнения ограничений (A*X <= B):")
    used_arr = A @ x_cont
    for i, (u, bi, sl) in enumerate(zip(used_arr, B, slack_cont), 1):
        ok = "✓" if sl >= -1e-9 else "✗"
        L.append(f"  строка {i}: {u:.4f} <= {bi:.0f},  зазор = {sl:.4f}  {ok}")

    # ── 3. Целочисленная задача ───────────────────────────────────
    hdr("Пункт 3. Решение задачи целочисленного программирования")
    L.append("Метод: ветвей и границ (scipy.optimize.milp)")
    L.append("")
    for p, xi in zip(PRODUCTS, x_int):
        L.append(f"  {p} = {int(xi)} ед.")
    L.append("")
    L.append(f"  F_max = {F_int:.0f} д.е.")
    L.append("")
    L.append("Загрузка ресурсов (целочисленный план):")
    for ri, used, sl, bi in zip(RESOURCES, A @ x_int, slack_int, B):
        L.append(f"  {ri}: использовано {used:.0f} из {bi:.0f},  остаток = {sl:.0f}")

    # ── 4. Двойственная задача ────────────────────────────────────
    hdr("Пункт 4. Постановка и решение двойственной задачи")
    L.append("Правила построения двойственной задачи:")
    L.append("  - Прямая задача: max F  =>  двойственная: min Z")
    L.append("  - Коэффициенты ЦФ прямой  => свободные члены ограничений двойственной")
    L.append("  - Свободные члены прямой  => коэффициенты ЦФ двойственной")
    L.append("  - Матрица ограничений транспонируется: A => A^T")
    L.append("  - Знаки неравенств меняются: <= => >=")
    L.append("")
    L.append("Математическая модель двойственной задачи:")
    L.append("")
    L.append("  Z = 21*y1 + 30*y2 + 16*y3  -->  min")
    L.append("")
    L.append("  Ограничения:")
    L.append("    3*y1 + 2*y2 + 0*y3 >= 3   (для Q1)")
    L.append("    1*y1 + 2*y2 + 3*y3 >= 2   (для Q2)")
    L.append("    y1, y2, y3 >= 0")
    L.append("")
    L.append("Решение двойственной задачи:")
    L.append("")
    for ri, yi in zip(RESOURCES, y):
        status = "дефицитный, ограничивает производство" if yi > 1e-6 \
                 else "избыточный, не является узким местом"
        L.append(f"  y({ri}) = {yi:.6f} д.е./ед.сырья  [{status}]")
    L.append("")
    L.append(f"  Z_min = {Z_min:.6f} д.е.")

    # ── 5. Проверка теоремы двойственности ───────────────────────
    hdr("Пункт 5. Проверка теоремы двойственности")
    L.append("По теореме двойственности оптимальные значения ЦФ прямой")
    L.append("и двойственной задач совпадают: F_max = Z_min")
    L.append("")
    L.append(f"  F_max (прямая задача)       = {F_cont:.6f}")
    L.append(f"  Z_min (двойственная задача) = {Z_min:.6f}")
    L.append(f"  Разность |F_max - Z_min|    = {abs(F_cont - Z_min):.2e}")
    L.append("")
    mark = "Теорема выполнена: F_max = Z_min  ✓" if duality_ok \
           else "ОШИБКА: расхождение значений  ✗"
    L.append(f"  {mark}")

    # ── 6. Экономическая интерпретация ───────────────────────────
    hdr("Пункт 6. Экономическая интерпретация результатов")
    scarce  = [r for r, s in zip(RESOURCES, slack_cont) if abs(s) < 1e-6]
    surplus = [r for r, s in zip(RESOURCES, slack_cont) if abs(s) >= 1e-6]
    L.append("Оптимальный план производства:")
    L.append(f"  Непрерывный:    " +
             ",  ".join(f"{p} = {v:.4f}" for p, v in zip(PRODUCTS, x_cont)))
    L.append(f"  Целочисленный:  " +
             ",  ".join(f"{p} = {int(v)}" for p, v in zip(PRODUCTS, x_int)))
    L.append("")
    L.append(f"  Максимальный доход (непрерывн.) = {F_cont:.4f} д.е.")
    L.append(f"  Максимальный доход (целочисл.)  = {F_int:.0f} д.е.")
    L.append("")
    L.append("Анализ ресурсов по теневым ценам:")
    L.append(f"  Дефицитные (yi > 0, использованы полностью): {', '.join(scarce)}")
    L.append(f"  Избыточные  (yi = 0, есть неиспользованный остаток): {', '.join(surplus)}")
    L.append("")
    L.append("Вывод:")
    L.append("  Для максимизации дохода следует производить:")
    L.append(f"    Q1 = {int(x_int[0])} ед.,  Q2 = {int(x_int[1])} ед.")
    L.append(f"  при этом доход составит {F_int:.0f} д.е.")
    L.append(f"  Ресурсы {', '.join(scarce)} являются узкими местами производства —")
    scarce_y = [f"{yi:.4f}" for ri, yi in zip(RESOURCES, y) if yi > 1e-6]
    L.append(f"  их расширение даст прирост дохода на {' и '.join(scarce_y)} д.е. за ед.")
    L.append(f"  Ресурс {', '.join(surplus)} не исчерпан, его расширение нецелесообразно.")

    L.append("")
    out_dir = Path(__file__).parent / "output" / "secondLab"
    dsep()
    L.append(f"Файл с результатами: {out_dir / 'Lab_rabota_2_stud_N16.txt'}")
    L.append("Все расчёты выполнены.")
    dsep()

    return "\n".join(L)


report = build_report()
print(report)

out_dir = Path(__file__).parent / "output" / "secondLab"
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / "Lab_rabota_2_stud_N16.txt"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(report + "\n")