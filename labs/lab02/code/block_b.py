"""ЛР2, блок B. Запуск: cd labs/lab02/code && python block_b.py"""

import numpy as np
from common import POLYGON, a, b, c, d, plot_transform

np.set_printoptions(precision=3, suppress=True)

plot_transform(np.array([[1, 1], [3, -2]]), "p06", title="Пункт 6")
plot_transform(np.array([[2, 1], [-3, 1]]), "p07", title="Пункт 7")
plot_transform(np.array([[1, 0], [1, -1]]), "p08", title="Пункт 8")
plot_transform(np.array([[2, 1], [1, 0]]), "p11", title="Пункт 11")
plot_transform(np.array([[2, 1], [0, 2]]), "p12", title="Пункт 12")
plot_transform(np.array([[3, 0], [0, 3]]), "p14", title="Пункт 14")
