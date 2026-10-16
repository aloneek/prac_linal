"""Общее для всей ЛР2. Ведёт Альберт. Остальные только импортируют:

    from common import a, b, c, d, POLYGON, plot_transform

Свои копии чисел в block_*.py не заводить — иначе картинки разъедутся.
"""
import sys
import numpy as np

sys.path.append('../../../template')
from plotstyle import setup, save, axes_2d  # noqa: E402

# --- Исходные данные (те же, что в draft.md) ---
a = 3
b = -2
c = 4
d = 5

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
    raise NotImplementedError
