"""ЛР2, блок A. Запуск: cd labs/lab02/code && python block_a.py"""
import numpy as np
from common import a, b, c, d, POLYGON, plot_transform

np.set_printoptions(precision=3, suppress=True)


def report(M, name):
    """Печать матрицы, собственных чисел и определителя — сверка с ручным расчётом."""
    lams, vecs = np.linalg.eig(M)
    print(f'--- {name} ---')
    print('M =\n', M)
    print('λ =', lams)
    print('векторы (по столбцам) =\n', vecs)
    print('det =', round(np.linalg.det(M), 3))


# Пункт 1. Отражение относительно y = ax.
# u = (1, a) лежит на прямой → остаётся на месте; w = (-a, 1) ⊥ прямой → переворачивается.
# M P = Q, где P = [u w], Q = [u -w]  →  M = Q P^{-1}
P = np.array([[1, -a],
              [a,  1]])
Q = np.array([[1,  a],
              [a, -1]])
M1 = Q @ np.linalg.inv(P)
report(M1, 'Пункт 1')
plot_transform(M1, 'p01', title='Пункт 1: отражение относительно $y = 3x$')



# Пункт 2. Ортогональная проекция на y = bx.
# u = (1, b) лежит на прямой → не меняется; w = (-b, 1) ⊥ прямой → схлопывается в 0.
P = np.array([[1, -b],
              [b,  1]])
Q = np.array([[1, 0],
              [b, 0]])
M2 = Q @ np.linalg.inv(P)
report(M2, 'Пункт 2')
print('M2 @ M2 == M2:', np.allclose(M2 @ M2, M2))
plot_transform(M2, 'p02', title='Пункт 2: проекция на $y = -2x$')


def rot(deg):
    """Матрица поворота на deg градусов против часовой: столбцы — образы (1,0) и (0,1)."""
    f = np.radians(deg)
    return np.array([[np.cos(f), -np.sin(f)],
                     [np.sin(f),  np.cos(f)]])


# Пункт 3. Поворот на 10c = 40° против часовой.
M3 = rot(10 * c)
report(M3, 'Пункт 3')
plot_transform(M3, 'p03', title='Пункт 3: поворот на 40° против часовой')

# Пункт 4. Центральная симметрия: v → -v для любого v, то есть M = -I (= поворот на 180°).
M4 = np.array([[-1.0, 0.0],
               [0.0, -1.0]])
report(M4, 'Пункт 4')
print('M4 == rot(180):', np.allclose(M4, rot(180)))
plot_transform(M4, 'p04', title='Пункт 4: центральная симметрия')

# Пункт 5. Сначала отражение M1, потом поворот на 10d = 140° по часовой (угол -140°).
# К вектору первой применяется правая матрица: M5 v = R(M1 v)  →  M5 = R @ M1.
M5 = rot(-10 * d) @ M1
report(M5, 'Пункт 5')
plot_transform(M5, 'p05', title='Пункт 5: отражение, затем поворот на 140° по часовой')
