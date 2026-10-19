"""Общее для всей ЛР2. Ведёт Альберт. Остальные только импортируют:

    from common import a, b, c, d, POLYGON, plot_transform

Свои копии чисел в block_*.py не заводить — иначе картинки разъедутся.
"""
import sys
import numpy as np
import matplotlib.pyplot as plt

import os

# Пути считаем от этого файла, а не от папки, откуда запущен python:
# так код работает и из code/, и по кнопке Run в VS Code из корня репо.
HERE = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(HERE, '..', 'figures')
sys.path.append(os.path.join(HERE, '..', '..', '..', 'template'))
from plotstyle import setup, save, axes_2d  # noqa: E402

setup()

# --- Исходные данные (те же, что в draft.md) ---
a = 3
b = -2
c = 4
d = 14

# Вершины многоугольника, по столбцам: shape (2, n)
# «Рыба»: A(-4,0) B(-2,1) C(0,1) D(1,0) E(3,3) F(3,-2) G(1,-1) H(-1,-2) I(-3,-1)
POLYGON = np.array([
    [-4, -2, 0, 1, 3,  3,  1, -1, -3],   # x
    [ 0,  1, 1, 0, 3, -2, -1, -2, -1],   # y
], dtype=float)


def plot_transform(M, name, title=None):
    """Нарисовать исходный POLYGON и его образ M @ POLYGON,
    добавить прямые вдоль вещественных собственных векторов M (если они есть),
    сохранить в figures/<name>.pdf через save().

    Интерфейс зафиксирован — остальные уже пишут код под него.
    Реализация — Альберт.
    """
    # asarray заодно превращает np.matrix и списки в обычный массив
    M = np.asarray(M, dtype=float)
    if M.shape != (2, 2):
        raise ValueError(f'plot_transform: нужна матрица 2×2, пришла {M.shape}')

    new = M @ POLYGON
    # Повторяем первую вершину в конце, чтобы контур замкнулся
    old_closed = np.hstack([POLYGON, POLYGON[:, :1]])
    new_closed = np.hstack([new, new[:, :1]])

    # Общие симметричные пределы: обе фигуры целиком, с запасом 15%
    L = 1.15 * np.abs(np.hstack([POLYGON, new])).max()

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot(old_closed[0], old_closed[1], label='исходная')
    ax.plot(new_closed[0], new_closed[1], label='образ')

    # Собственные векторы — столбцы vecs; комплексные λ (поворот) пропускаем
    lams, vecs = np.linalg.eig(M)
    t = np.linspace(-L, L, 2)
    for i in range(2):
        if not np.isreal(lams[i]):
            continue
        v = vecs[:, i].real
        ax.plot(t * v[0], t * v[1], '--', linewidth=1.2,
                label=f'λ = {lams[i].real:.2f}')

    axes_2d(ax, lim=L)
    if title:
        ax.set_title(title)
    ax.legend(loc='best', fontsize=9)
    save(fig, name, figures_dir=FIG_DIR)
    plt.close(fig)


if __name__ == '__main__':
    plot_transform(np.array([[1, 2], [3, 5]]), 'test')
    plot_transform(np.array([[0, -1], [1, 0]]), 'test_rot', title='поворот на 90°')
