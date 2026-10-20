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
