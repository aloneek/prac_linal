"""ЛР2, блок B. Запуск: cd labs/lab02/code && python block_b.py"""

import numpy as np
from common import POLYGON, a, b, c, d, plot_transform

np.set_printoptions(precision=3, suppress=True)

#9. Отображение, образованное недиагональной матрицей, которое переводит круг
#единичной площади с центром в начале координат в круг площади c.
c=12
plot_transform(np.array([[np.cos(np.pi/6)*np.sqrt(c), -np.sin(np.pi/6)*np.sqrt(c)], 
                         [np.sin(np.pi/6)*np.sqrt(c), np.cos(np.pi/6)*np.sqrt(c)]]), 
                         "p09", 
                         title="Пункт 9",)

plot_transform(np.array([[np.cos(np.pi/6)*np.sqrt(c), -np.sin(np.pi/6)*np.sqrt(c)], 
                         [np.sin(np.pi/6)*np.sqrt(c), np.cos(np.pi/6)*np.sqrt(c)]]), 
                         "p09c", 
                         title="Пункт 9",
                         POLYGON=np.array([[np.cos(t)*np.sqrt(1/np.pi), np.sin(t)*np.sqrt(1/np.pi)] for t in np.linspace(0, 2*np.pi, 100)]).T)

#10. Отображение, образованное недиагональной матрицей, которое переводит круг
#единичной площади с центром в начале координат в некруг площади d.
d=3
plot_transform(np.array([[3, 8], [0, 1]]), "p10c", title="Пункт 10")
plot_transform(np.array([[3, 8], [0, 1]]), "p10c", title="Пункт 10",
               POLYGON=np.array([[np.cos(t)*np.sqrt(1/np.pi), np.sin(t)*np.sqrt(1/np.pi)] for t in np.linspace(0, 2*np.pi, 100)]).T)


#13. Отображение, образованное вещественной матрицей, у которого нет ни одного
#вещественного собственного вектора
plot_transform(np.array([[0, -1], [1, 0]]), "p13", title="Пункт 13")

#15. Пару отображений, последовательное применение которых даёт различные результаты в зависимости от порядка: AB ̸= BA. Сделайте визуализацию всех рассматриваемых отображений, а именно: A, B, AB и BA.
A=np.array([[1, 1], [0, 1]])
B=np.array([[2, 1], [0, 1]])
plot_transform(A, "p15A", title="Пункт 15")
plot_transform(B, "p15B", title="Пункт 15") 
plot_transform(A@B, "p15AB", title="Пункт 15")
plot_transform(B@A, "p15BA", title="Пункт 15")

#16. Пару отображений, последовательное применение которых даёт одинаковый результат независимо от порядка: AB = BA. Постарайтесь, чтобы матрицы A и B
#были максимально непохожими друг на друга. Сделайте визуализацию, аналогичную предыдущему пункту.
A=np.array([[1, 1], [0, 1]])
B=np.array([[3, -2], [0, 3]])
plot_transform(A@B, "p16AB", title="Пункт 16")
plot_transform(B@A, "p16BA", title="Пункт 16")
