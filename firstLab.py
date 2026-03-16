"""
Лабораторная работа 1
Оптимизация и математические методы принятия решений
"""

import os
import numpy as np
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ─── ЗАПРОС ВАРИАНТА ──────────────────────────────────────────
try:
    n = int(input("Введите номер варианта (1-30): "))
except ValueError:
    n = 16
    print("Ошибка ввода. Использован вариант по умолчанию: 16")

# Определяем режим решения (стр. 14 методички)
# "для нечетных вариантов — MIN, для четных вариантов — MAX"
MODE = "MAX" if n % 2 == 0 else "MIN"

OUTPUT_DIR = os.path.join("output", f"firstLab_v{n}")
os.makedirs(OUTPUT_DIR, exist_ok=True)

TXT_PATH = os.path.join(OUTPUT_DIR, f"Lab_rabota_1_stud_N{n}.txt")


# ─── вспомогательные функции ──────────────────────────────────
# (оставляем ваши функции без изменений)
def mat2str(m, fmt='{:10.4f}'):
    m = np.atleast_2d(m)
    return '\n'.join('  ' + '  '.join(fmt.format(v) for v in row) for row in m)


def minor(M, i, j):
    sub = np.delete(np.delete(M, i, axis=0), j, axis=1)
    return np.linalg.det(sub)


def algdop(M, i, j):
    return ((-1) ** (i + j)) * minor(M, i, j)


def gauss_jordan(A, B):
    mat = np.hstack([A, B]).astype(float)
    nr, nc = mat.shape
    pivot_row = 0
    for col in range(nc - 1):
        max_row = np.argmax(np.abs(mat[pivot_row:, col])) + pivot_row
        if abs(mat[max_row, col]) < 1e-12:
            continue
        mat[[pivot_row, max_row]] = mat[[max_row, pivot_row]]
        mat[pivot_row] /= mat[pivot_row, col]
        for row in range(nr):
            if row != pivot_row:
                mat[row] -= mat[row, col] * mat[pivot_row]
        pivot_row += 1
    return mat


def write(f, text=''):
    print(text)
    f.write(text + '\n')


# ══════════════════════════════════════════════════════════════
with open(TXT_PATH, 'w', encoding='utf-8') as f:
    write(f, '=' * 70)
    write(f, f'Лабораторная работа 1. ВАРИАНТ №{n}')
    write(f, f'Режим поиска целевой функции: {MODE}')
    write(f, '=' * 70)

    # ─────────────────────────────────────────────────────────
    # Пункт 1. Исходные матрицы A и B
    # ─────────────────────────────────────────────────────────
    write(f, '\n' + '─' * 70)
    write(f, 'Пункт 1. Исходные матрицы A и B')
    write(f, '─' * 70)

    Aish = np.array([
        [3, 4, 3, 8, 9],
        [5, 2, 1, 4, 3],
        [4, 9, 4, 6, 7],
        [3, 4, 11, 5, 4],
        [8, 9, 8, 7, 1]
    ], dtype=float)
    Bish = np.array([[61], [43], [79], [87], [58]], dtype=float)

    # Формирование данных согласно варианту (стр. 10 методички)
    A = Aish + (2 * n - 1)
    B = Bish + (9 * n - 4)

    # ... ДАЛЕЕ ВАШ КОД БЕЗ ИЗМЕНЕНИЙ ДО 12 ПУНКТА ...

    write(f, '\nМатрица A (5×5):')
    write(f, mat2str(A, '{:5.0f}'))
    write(f, '\nМатрица B (5×1):')
    write(f, mat2str(B, '{:5.0f}'))

    # ─────────────────────────────────────────────────────────
    # Пункт 2. Транспонирование матриц A и B
    # ─────────────────────────────────────────────────────────
    write(f, '\n' + '─' * 70)
    write(f, 'Пункт 2. Транспонирование матриц A и B')
    write(f, '─' * 70)

    At = A.T
    Bt = B.T

    write(f, '\nТранспонированная матрица At (5×5):')
    write(f, mat2str(At, '{:5.0f}'))
    write(f, '\nТранспонированная матрица Bt (1×5):')
    write(f, mat2str(Bt, '{:5.0f}'))

    # ─────────────────────────────────────────────────────────
    # Пункт 3. Обратная матрица A и проверка A * A^(-1) = E
    # ─────────────────────────────────────────────────────────
    write(f, '\n' + '─' * 70)
    write(f, 'Пункт 3. Обратная матрица A и проверка')
    write(f, '─' * 70)

    Aobr  = np.linalg.inv(A)
    provA = A @ Aobr

    write(f, '\nОбратная матрица A^(-1):')
    write(f, mat2str(Aobr, '{:12.5e}'))
    write(f, '\nПроверка A * A^(-1) = E:')
    write(f, mat2str(provA, '{:8.4f}'))

    # ─────────────────────────────────────────────────────────
    # Пункт 4. Проверка матрицы A на ортогональность
    # ─────────────────────────────────────────────────────────
    write(f, '\n' + '─' * 70)
    write(f, 'Пункт 4. Проверка матрицы A на ортогональность')
    write(f, 'Условие: At - A^(-1) = [0]')
    write(f, '─' * 70)

    Eort      = At - Aobr
    norm_eort = np.linalg.norm(Eort)

    write(f, '\nРазность At - A^(-1):')
    write(f, mat2str(Eort, '{:10.4f}'))
    write(f, f'\nНорма ||At - A^(-1)|| = {norm_eort:.6f}')
    if norm_eort < 1e-9:
        write(f, 'Вывод: матрица A является ортогональной.')
    else:
        write(f, 'Вывод: матрица A НЕ является ортогональной (норма ≠ 0).')

    # ─────────────────────────────────────────────────────────
    # Пункт 5. Матрица нормированных коэффициентов C = fnorm(Bt)
    # ─────────────────────────────────────────────────────────
    write(f, '\n' + '─' * 70)
    write(f, 'Пункт 5. Матрица нормированных коэффициентов C = fnorm(Bt)')
    write(f, 'Формула: C_i = (Bt_i - min(Bt)) / (max(Bt) - min(Bt))')
    write(f, '─' * 70)

    Bt_flat = Bt.flatten()
    Bt_min  = Bt_flat.min()
    Bt_max  = Bt_flat.max()
    C = ((Bt_flat - Bt_min) / (Bt_max - Bt_min)).reshape(1, -1)

    write(f, f'\nmin(Bt) = {Bt_min:.0f},  max(Bt) = {Bt_max:.0f}')
    write(f, '\nМатрица нормированных коэффициентов C (1×5):')
    write(f, mat2str(C, '{:.6f}'))

    # ─────────────────────────────────────────────────────────
    # Пункт 6. Умножение матриц [C*B] и [B*C]
    # ─────────────────────────────────────────────────────────
    write(f, '\n' + '─' * 70)
    write(f, 'Пункт 6. Умножение матриц [C*B] и [B*C]')
    write(f, '─' * 70)

    Fcb = C @ B
    Fbc = B @ C

    write(f, f'\nРезультат C * B (скаляр): {Fcb[0, 0]:.6f}')
    write(f, '\nРезультат B * C (матрица 5×5):')
    write(f, mat2str(Fbc, '{:12.4f}'))

    # ─────────────────────────────────────────────────────────
    # Пункт 7. Определители матриц [B*C] и A
    # ─────────────────────────────────────────────────────────
    write(f, '\n' + '─' * 70)
    write(f, 'Пункт 7. Определители матриц [B*C] и A')
    write(f, '─' * 70)

    det_Fbc = np.linalg.det(Fbc)
    det_A   = np.linalg.det(A)

    write(f, f'\ndet(B*C) = {det_Fbc:.6e}')
    write(f,  '  Пояснение: det(B*C) = 0, т.к. ранг матрицы B*C равен 1')
    write(f,  '  (все столбцы B*C пропорциональны столбцу B — линейно зависимы).')
    write(f, f'\ndet(A) = {det_A:.6f}')
    write(f, f'  Пояснение: det(A) ≠ 0, матрица A невырождена и обратима.')

    # ─────────────────────────────────────────────────────────
    # Пункт 8. Главные (угловые) миноры матрицы A
    #          + алгебраические дополнения всех элементов
    #
    # Угловой минор Δk вычисляется ВЫЧЕРКИВАНИЕМ строк (k+1..n)
    # и столбцов (k+1..n) из матрицы A:
    #   sub = np.delete(np.delete(A, rows_k+1..n, axis=0), cols_k+1..n, axis=1)
    # ─────────────────────────────────────────────────────────
    write(f, '\n' + '─' * 70)
    write(f, 'Пункт 8. Главные (угловые) миноры матрицы A')
    write(f, 'Метод: вычёркивание строк и столбцов с (k+1) по n')
    write(f, '─' * 70)

    write(f, '\nИсходная матрица A:')
    write(f, mat2str(A, '{:5.0f}'))

    write(f, '\nГлавные (угловые) миноры Δk:')
    for k in range(1, 6):
        i_del = k - 1   # индекс строки для удаления (0-based)
        j_del = k - 1   # индекс столбца для удаления (0-based)

        sub = np.delete(np.delete(A, i_del, axis=0), j_del, axis=1)
        dk  = np.linalg.det(sub)

        write(f, f'\n  Δ{k}: вычёркиваем строку {k} и столбец {k}')
        write(f, f'  Подматрица {sub.shape[0]}×{sub.shape[1]}:')
        write(f, mat2str(sub, '{:5.0f}'))
        write(f, f'  det Δ{k} = {dk:.4f}')

    write(f, '\n' + '─' * 40)
    write(f, 'Алгебраические дополнения всех элементов матрицы A:')
    write(f, '')
    write(f, '  Минор M(i,j)           = det(A без строки i и столбца j)')
    write(f, '  Алг. дополнение A(i,j) = (-1)^(i+j) * M(i,j)')

    for i in range(5):
        for j in range(5):
            aij  = A[i, j]
            sub  = np.delete(np.delete(A, i, axis=0), j, axis=1)
            Mij  = np.linalg.det(sub)
            sign = (-1) ** (i + j)
            Aij  = sign * Mij

            write(f, '')
            write(f, f'  ── Элемент a({i+1},{j+1}) = {aij:.0f}  │  удаляем строку {i+1} и столбец {j+1}')
            write(f, f'  Подматрица {A.shape[0]-1}×{A.shape[1]-1}:')
            write(f, mat2str(sub, '{:6.0f}'))
            write(f, f'  Минор    M({i+1},{j+1}) = det = {Mij:.4f}')
            write(f, f'  Знак     (-1)^({i+1}+{j+1}) = {sign:+d}')
            write(f, f'  Алг. доп. A({i+1},{j+1}) = {sign:+d} * ({Mij:.4f}) = {Aij:.4f}')

    check = sum(A[i, 0] * algdop(A, i, 0) for i in range(5))
    write(f, f'\nПроверка разложением по 1-му столбцу:')
    write(f, f'  Σ a(i,1) * A(i,1) = {check:.4f}')
    write(f, f'  det(A)             = {det_A:.4f}')
    write(f, f'  {"Совпадает ✓" if abs(check - det_A) < 1e-4 else "ОШИБКА!"}')

    # ─────────────────────────────────────────────────────────
    # Пункт 9. Решение СЛАУ Ax=B методом Гаусса
    # ─────────────────────────────────────────────────────────
    write(f, '\n' + '─' * 70)
    write(f, 'Пункт 9. Решение СЛАУ Ax=B методом Гаусса')
    write(f, '─' * 70)

    AB_rref = gauss_jordan(A, B)
    XGs     = AB_rref[:, -1]
    EpsGs   = A @ XGs.reshape(-1, 1) - B

    write(f, '\nРасширенная матрица [A|B] после приведения к RREF:')
    write(f, mat2str(AB_rref, '{:9.4f}'))
    write(f, '\nВектор решений X:')
    for i, xi in enumerate(XGs):
        write(f, f'  x{i+1} = {xi:.8f}')
    write(f, '\nПроверка невязки (A*X - B):')
    write(f, mat2str(EpsGs, '{:.3e}'))

    # ─────────────────────────────────────────────────────────
    # Пункт 10. Решение СЛАУ Ax=B методом обратной матрицы
    # ─────────────────────────────────────────────────────────
    write(f, '\n' + '─' * 70)
    write(f, 'Пункт 10. Решение СЛАУ Ax=B методом обратной матрицы')
    write(f, 'Формула: X = A^(-1) * B')
    write(f, '─' * 70)

    Xom   = Aobr @ B
    Epsom = A @ Xom - B

    write(f, '\nВектор решений X = A^(-1) * B:')
    for i, xi in enumerate(Xom.flatten()):
        write(f, f'  x{i+1} = {xi:.8f}')
    write(f, '\nПроверка невязки (A*X - B):')
    write(f, mat2str(Epsom, '{:.3e}'))

    # ─────────────────────────────────────────────────────────
    # Пункт 11. График функции принадлежности
    # ─────────────────────────────────────────────────────────
    write(f, '\n' + '─' * 70)
    write(f, 'Пункт 11. Функция принадлежности μ(AA)')
    write(f, f'Формула: μ(AA) = (AA - 1) / (AA * (n+39)/(n+31)),  n={n}')
    write(f, '─' * 70)

    AAx    = np.arange(1, 26)
    muAAx  = (AAx - 1) / (AAx * (n + 39) / (n + 31))

    AAx_plot   = np.concatenate([[0, 0.99], AAx])
    muAAx_plot = np.concatenate([[0, 0],    muAAx])

    fig1, ax1 = plt.subplots(figsize=(8, 3))
    ax1.plot(AAx_plot, muAAx_plot, 'b', linewidth=2.5)
    ax1.set_xticks([0, 5, 10, 15, 20, 25])
    ax1.set_xlim(0, 25)
    ax1.set_yticks([0, 0.25, 0.5, 0.75, 1])
    ax1.set_ylim(0, 1)
    ax1.grid(True)
    ax1.set_xlabel('AA', fontsize=13)
    ax1.set_ylabel('μ(AA)', fontsize=13)
    ax1.set_title(f'Функция принадлежности μ(AA), вариант {n}')
    plt.tight_layout()

    graf_path = os.path.join(OUTPUT_DIR, f'Graf_LabRab_1_v{n}.png')
    fig1.savefig(graf_path, dpi=120)
    plt.close(fig1)

    write(f, f'\nГрафик сохранён: {graf_path}')

    write(f, '\nТаблица значений μ(AA):')
    write(f, f'  {"AA":>4}  {"μ(AA)":>8}')
    for aa, mu in zip(AAx, muAAx):
        write(f, f'  {aa:4.0f}  {mu:8.6f}')

    # ─────────────────────────────────────────────────────────
    # Пункт 12. Целевая функция — графическое решение
    # ─────────────────────────────────────────────────────────
    write(f, '\n' + '─' * 70)
    write(f, 'Пункт 12. Графическое решение целевой функции (MAX, вариант 16)')
    write(f, '─' * 70)

    k = round(((32 - n) / (41 - n)) * n)
    w = round((n - k + 6) / (n + 1))

    write(f, f'\nПараметры: k = {k},  w = {w}')
    write(f, f'V1(t) = {k} * cos({w}*t) + ({n}/{n+3}) * cos(3*{w}*t)')
    write(f, f'V2(t) = {k//2} + {w}*t - 1')
    write(f,  'Область определения: -4π ≤ t ≤ 3π')

    t  = np.arange(-4 * np.pi, 3 * np.pi + 0.01, 0.01)
    V1 = k * np.cos(w * t) + (n / (n + 3)) * np.cos(3 * w * t)
    V2 = k / 2 + w * t - 1

    diff         = V1 - V2
    sign_changes = np.where(np.diff(np.sign(diff)))[0]
    crossings    = []
    for idx in sign_changes:
        t_cross = t[idx] - diff[idx] * (t[idx+1] - t[idx]) / (diff[idx+1] - diff[idx])
        crossings.append(t_cross)

    mask = V1 >= V2
    if mask.any():
        best_idx = np.argmax(V1[mask])
        t_opt    = t[mask][best_idx]
        f_max    = V1[mask][best_idx]
    else:
        t_opt = t[np.argmax(V1)]
        f_max = V1.max()

    write(f, f'\nРезультат:  F_max = {f_max:.6f}  при t = {t_opt:.6f} рад')
    write(f,  '\nТочки пересечения V1(t) = V2(t):')
    for tc in crossings:
        write(f, f'  t = {tc:8.4f} рад  ({tc/np.pi:.4f}π)')

    fig2, ax2 = plt.subplots(figsize=(9, 4))
    ax2.plot(t / np.pi, V1, 'b', linewidth=2,
             label=f'V1 = {k}·cos({w}t) + {n}/{n+3}·cos(3t)')
    ax2.plot(t / np.pi, V2, 'g', linewidth=2,
             label=f'V2 = {k//2} + {w}·t − 1')
    ax2.fill_between(t / np.pi, V1, V2, where=mask,
                     alpha=0.15, color='blue', label='V1 ≥ V2 (допустимая область)')
    ax2.axvline(t_opt / np.pi, color='r', linestyle='--', linewidth=1.5,
                label=f'MAX ≈ {f_max:.2f}  при t ≈ {t_opt/np.pi:.3f}π')
    ax2.scatter([t_opt / np.pi], [f_max], color='red', zorder=5, s=80)
    for tc in crossings:
        ax2.axvline(tc / np.pi, color='orange', linestyle=':', linewidth=0.8, alpha=0.7)
    ax2.grid(True)
    ax2.legend(fontsize=8, loc='upper left')
    ax2.set_xlabel('t / π', fontsize=12)
    ax2.set_ylabel('F(t)', fontsize=12)
    ax2.set_title(f'Графическое решение целевой функции (MAX), вариант {n}')
    ax2.set_xlim(-4, 3)
    plt.tight_layout()

    resh_path = os.path.join(OUTPUT_DIR, f'Resh_LabRab_1_v{n}.png')
    fig2.savefig(resh_path, dpi=120)
    plt.close(fig2)

    write(f, f'\nГрафик сохранён: {resh_path}')

    write(f, '\n' + '=' * 70)
    write(f, f'Файл с результатами: {TXT_PATH}')
    write(f, 'Все расчёты выполнены.')