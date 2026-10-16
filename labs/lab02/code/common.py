"""Общее для всей ЛР2. Ведёт Альберт. Остальные только импортируют:

    from common import a, b, c, d, POLYGON, plot_transform

Свои копии чисел в block_*.py не заводить — иначе картинки разъедутся.
"""
import sys
import numpy as np

sys.path.append('../../../template')
from plotstyle import setup, save, axes_2d  # noqa: E402

# --- Исходные данные (те же, что в draft.md) ---
a = None  # TODO: выбрать вместе
b = None
c = None
d = None

# Вершины многоугольника, по столбцам: shape (2, n)
POLYGON = None  # TODO


def plot_transform(M, name, title=None):
    """Нарисовать исходный POLYGON и его образ M @ POLYGON,
    добавить прямые вдоль вещественных собственных векторов M (если они есть),
    сохранить в figures/<name>.pdf через save().

    Интерфейс зафиксирован — остальные уже пишут код под него.
    Реализация — Альберт.
    """
    raise NotImplementedError
