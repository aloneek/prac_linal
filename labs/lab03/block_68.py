"""ЛР3, задания 6-8. Камера, перспектива и домик из блоков.

Запуск: python block_68.py
Рисунки сохраняются в labs/lab03/figures/.
Все преобразования координат — умножение на матрицы 4x4.
Matplotlib рисует в режиме proj_type="ortho" и своей перспективы не добавляет.
"""

import ast
import sys
from pathlib import Path
from types import SimpleNamespace

import matplotlib.pyplot as plt
import numpy as np

LAB = Path(__file__).resolve().parent
FIGURES_DIR = LAB / "figures"

np.set_printoptions(precision=3, suppress=True)

# ---------- Функции из блоков коллег ----------

# Блок A (Альберт): куб из методички, отрисовка фигуры, пределы осей.
sys.path.append(str(LAB / "code"))
from block_a import draw_shape, faces_cube, set_scene_axes, vertices_cube  # noqa: E402


def load_functions(path):
    """Взять из скрипта только функции, не запуская его расчёты.

    block_45.py (Слава) при импорте сразу считает задания 4-5 и перезаписывает
    свои рисунки, поэтому выполняем из него лишь import-строки и def-определения.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    tree.body = [node for node in tree.body
                 if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef))]
    namespace = {}
    exec(compile(tree, str(path), "exec"), namespace)
    return SimpleNamespace(**namespace)


# Задания 4-5 (Слава): перенос, поворот e^{J theta}, ось и угол по матрице.
block_45 = load_functions(LAB / "block_45.py")
translation_matrix = block_45.translation_matrix
rotation_matrix = block_45.rotation_matrix


def scale_matrix(sx, sy, sz):
    """Матрица масштаба из задания 2."""
    return np.diag([sx, sy, sz, 1.0])


# ---------- Общие функции отрисовки ----------

# Фигура сцены — тройка (вершины 4xN, грани, цвет).


def transform_scene(scene, M):
    """Применить одну матрицу ко всем фигурам сцены."""
    return [(M @ vertices, faces, color) for vertices, faces, color in scene]


def scene_vertices(scene):
    return [vertices for vertices, _, _ in scene]


def draw_scene(ax, scene, alpha=0.9):
    for vertices, faces, color in scene:
        draw_shape(ax, vertices, faces, color, alpha=alpha)


def new_figure(title, vertices_list, elev=25, azim=-60):
    """Окно с одинаковым масштабом по осям и заданным ракурсом."""
    fig = plt.figure(figsize=(6.5, 6.5))
    ax = fig.add_subplot(projection="3d", proj_type="ortho")
    set_scene_axes(ax, *vertices_list)
    ax.view_init(elev=elev, azim=azim)
    if elev == -90:
        ax.set_zticks([])  # ось z смотрит на зрителя, подписи слились бы в точку
    ax.set_title(title)
    return fig, ax


def save(fig, name):
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / f"{name}.png"
    fig.savefig(path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"Сохранено: {path}")


# ---------- Задание 6. Сцена и камера ----------

# Сцена: четыре кубика, у каждого своя матрица M = T R S
# (сначала масштаб, потом поворот, потом перенос).
M_red_cube = translation_matrix([-3.0, -1.0, 1.0])
M_green_cube = (translation_matrix([2.0, 0.0, 1.5])
                @ rotation_matrix([0, 0, 1], np.radians(30))
                @ scale_matrix(1.5, 1.5, 1.5))
M_blue_cube = (translation_matrix([0.0, 4.0, 1.4])
               @ rotation_matrix([1, 1, 0], np.radians(45))
               @ scale_matrix(0.8, 0.8, 0.8))
M_yellow_cube = translation_matrix([-1.0, 2.0, 0.5]) @ scale_matrix(2.0, 0.5, 0.5)

scene6 = [
    (M_red_cube @ vertices_cube, faces_cube, "tab:red"),
    (M_green_cube @ vertices_cube, faces_cube, "tab:green"),
    (M_blue_cube @ vertices_cube, faces_cube, "tab:blue"),
    (M_yellow_cube @ vertices_cube, faces_cube, "gold"),
]

# Два ракурса: стандартный и запрошенный заданием.
fig, ax = new_figure("Сцена: стандартный ракурс", scene_vertices(scene6))
draw_scene(ax, scene6)
save(fig, "p6_scene")

fig, ax = new_figure("Сцена: view_init(azim=0, elev=-90)", scene_vertices(scene6),
                     elev=-90, azim=0)
draw_scene(ax, scene6)
save(fig, "p6_bottom")


# Камера. Стандартная камера стоит в начале координат и смотрит вдоль +z,
# её ось x — вверх по кадру, ось y — вправо. Ровно так matplotlib
# показывает график при view_init(azim=0, elev=-90).
def camera_rotation(position, target):
    """R_c: столбцы — оси камеры (вверх, вправо, вперёд) в мировых координатах."""
    forward = (target - position) / np.linalg.norm(target - position)
    right = np.cross(forward, [0, 0, 1])
    right = right / np.linalg.norm(right)
    up = np.cross(right, forward)
    Rc = np.eye(4)
    Rc[:3, :3] = np.column_stack([up, right, forward])
    return Rc


def inverse_camera(Rc, position):
    """C^-1 = R_c^T T(-c): обратные множители в обратном порядке."""
    Rc_inv = np.eye(4)
    Rc_inv[:3, :3] = Rc[:3, :3].T  # обратная к повороту — транспонированная
    return Rc_inv @ translation_matrix(-position)


def draw_camera(ax, C, size=2.0):
    """Точка камеры и стрелки её осей x_c, y_c, z_c (столбцы матрицы C)."""
    position = C[:3, 3]
    ax.scatter(*position, color="k")
    for i, (color, label) in enumerate([("tab:red", "$x_c$"), ("tab:green", "$y_c$"),
                                        ("tab:blue", "$z_c$")]):
        arrow = size * C[:3, i]
        ax.quiver(*position, *arrow, color=color, linewidth=2)
        ax.text(*(position + 1.15 * arrow), label, color=color)


camera_position = np.array([9.0, -7.0, 8.0])
camera_target = np.array([0.0, 1.0, 0.5])

Tc = translation_matrix(camera_position)
Rc = camera_rotation(camera_position, camera_target)
C = Tc @ Rc

camera_axis = block_45.rotation_axis_from_matrix(Rc)
camera_angle = block_45.rotation_angle_from_matrix(Rc)
print(f"T_c =\n{Tc}\n")
print(f"R_c =\n{Rc}\n")
print(f"R_c — поворот на {camera_angle:.2f}° вокруг оси {camera_axis}")
print("R_c = exp(J theta):",
      np.allclose(rotation_matrix(camera_axis, np.radians(camera_angle)), Rc))
block_45.check_rotation("R_c", Rc, camera_axis)
print(f"C = T_c R_c =\n{C}\n")

C_inv = inverse_camera(Rc, camera_position)
print(f"C^-1 = R_c^T T(-c) =\n{C_inv}\n")
print("C C^-1 = I:", np.allclose(C @ C_inv, np.eye(4)))
print("Камера после C^-1:", (C_inv @ np.append(camera_position, 1))[:3])
print("Цель после C^-1 (на оси +z):", (C_inv @ np.append(camera_target, 1))[:3])
print()

fig, ax = new_figure("Сцена и камера C", scene_vertices(scene6) + [C[:, 3:]])
draw_scene(ax, scene6)
draw_camera(ax, C)
ax.plot(*np.column_stack([camera_position, camera_target]), "k--", linewidth=0.8)
save(fig, "p6_camera")

# Сцена глазами камеры: C^-1 ко всем объектам.
scene_camera = transform_scene(scene6, C_inv)
depth = np.hstack(scene_vertices(scene_camera))[2]
print(f"Глубина сцены после C^-1: z от {depth.min():.2f} до {depth.max():.2f}\n")

origin = np.array([[0.0], [0.0], [0.0], [1.0]])
fig, ax = new_figure("После $C^{-1}$: стандартный ракурс",
                     scene_vertices(scene_camera) + [origin])
draw_scene(ax, scene_camera)
draw_camera(ax, np.eye(4))
save(fig, "p6_inv")

fig, ax = new_figure("После $C^{-1}$: view_init(azim=0, elev=-90)",
                     scene_vertices(scene_camera) + [origin], elev=-90, azim=0)
draw_scene(ax, scene_camera)
draw_camera(ax, np.eye(4))
save(fig, "p6_inv_bottom")


# ---------- Задание 7. Перспектива ----------

def perspective_matrix(l, r, b, t, n, f):
    """Матрица перспективы для камеры, смотрящей вдоль +z.

    Пирамида видимости между плоскостями z = n и z = f переходит в куб [-1, 1]^3.
    Последняя строка (0, 0, 1, 0) записывает глубину z в четвёртую координату.
    """
    return np.array([
        [2 * n / (r - l), 0, -(r + l) / (r - l), 0],
        [0, 2 * n / (t - b), -(t + b) / (t - b), 0],
        [0, 0, (f + n) / (f - n), -2 * f * n / (f - n)],
        [0, 0, 1, 0],
    ])


def piramida_vidimosti(n, f, polurazmer):
    """Вершины пирамиды видимости в координатах камеры.

    Порядок вершин тот же, что у куба: грань куба z = -1 -> ближняя плоскость n,
    грань z = 1 -> дальняя f. Поэтому грани пирамиды — те же faces_cube.
    """
    z = np.where(vertices_cube[2] < 0, n, f)
    k = polurazmer * z / n  # половина стороны сечения растёт пропорционально z
    return np.vstack([vertices_cube[0] * k, vertices_cube[1] * k, z, np.ones(8)])


# Частный случай: симметричная квадратная пирамида.
n, f = 4.0, 25.0
ugol_obzora = np.radians(50.0)
polurazmer = n * np.tan(ugol_obzora / 2)  # половина стороны кадра на плоскости z = n
P = perspective_matrix(-polurazmer, polurazmer, -polurazmer, polurazmer, n, f)
print(f"P =\n{P}\n")

scene_persp = transform_scene(scene6, P @ C_inv)
persp_all = np.hstack(scene_vertices(scene_persp))
persp_points = persp_all[:3] / persp_all[3]
print("w' совпадает с глубиной z после C^-1:", np.allclose(persp_all[3], depth))
print("Все вершины внутри куба [-1,1]^3:", np.all(np.abs(persp_points) <= 1))
print(f"z' вершин: от {persp_points[2].min():.3f} до {persp_points[2].max():.3f}\n")

# Изометрическая камера и перспектива: одна сцена, вид камеры.
fig, ax = new_figure("Изометрия: $C^{-1}$, вид камеры", scene_vertices(scene_camera),
                     elev=-90, azim=0)
draw_scene(ax, scene_camera)
save(fig, "p7_iso")

fig, ax = new_figure("Перспектива: $P\\,C^{-1}$, вид камеры", [vertices_cube],
                     elev=-90, azim=0)
draw_scene(ax, scene_persp)
save(fig, "p7_persp")

# Деформация пространства: пирамида видимости до P и её образ (куб) после P.
piramida = piramida_vidimosti(n, f, polurazmer)
for i, (elev, azim) in enumerate([(25, -60), (10, -120)], 1):
    fig, ax = new_figure(f"До $P$: пирамида видимости, ракурс {i}",
                         scene_vertices(scene_camera) + [piramida], elev, azim)
    draw_scene(ax, scene_camera)
    draw_shape(ax, piramida, faces_cube, "none")
    draw_camera(ax, np.eye(4))
    save(fig, f"p7_before{i}")

    fig, ax = new_figure(f"После $P$: куб $[-1,1]^3$, ракурс {i}", [P @ piramida], elev, azim)
    draw_scene(ax, scene_persp)
    draw_shape(ax, P @ piramida, faces_cube, "none")
    save(fig, f"p7_after{i}")


# ---------- Задание 8. Домик ----------

# Треугольная призма для крыши: треугольник (y, z) = (-1, 0), (1, 0), (0, 1),
# вытянутый вдоль x от -1 до 1. Треугольные грани записаны четвёрками
# с повтором вершины, чтобы все грани были одной длины, как у куба.
vertices_prism = np.array([
    [-1, -1, -1, 1, 1, 1],
    [-1, 1, 0, -1, 1, 0],
    [0, 0, 1, 0, 0, 1],
    [1, 1, 1, 1, 1, 1],
])
faces_prism = np.array([
    [0, 1, 2, 2],  # торец x = -1
    [3, 4, 5, 5],  # торец x = 1
    [0, 1, 4, 3],  # основание
    [1, 2, 5, 4],  # скат
    [2, 0, 3, 5],  # скат
])

# Детали дома в его собственной системе координат, пол дома — плоскость z = 0.
# Стены 6 x 5 x 3; крыша выступает за стены на sves = 0.3 с каждой стороны.
sves = 0.3
walls = translation_matrix([0, 0, 1.5]) @ scale_matrix(3, 2.5, 1.5)
roof = translation_matrix([0, 0, 3]) @ scale_matrix(3 + sves, 2.5 + sves, 2.1)
door = translation_matrix([1.6, -2.55, 0.9]) @ scale_matrix(0.5, 0.05, 0.9)
window_front = translation_matrix([-1.2, -2.55, 1.8]) @ scale_matrix(0.6, 0.05, 0.45)
window_side = translation_matrix([3.05, 0, 1.8]) @ scale_matrix(0.05, 0.7, 0.45)

house = [
    (walls @ vertices_cube, faces_cube, "wheat"),
    (roof @ vertices_prism, faces_prism, "firebrick"),
    (door @ vertices_cube, faces_cube, "saddlebrown"),
    (window_front @ vertices_cube, faces_cube, "lightskyblue"),
    (window_side @ vertices_cube, faces_cube, "lightskyblue"),
]

# Весь дом ставится в сцену одной матрицей: поворот на 20° и перенос.
M_house = translation_matrix([1.0, 0.5, 0.0]) @ rotation_matrix([0, 0, 1], np.radians(20))
print(f"M_house =\n{M_house}\n")

tree_trunk = translation_matrix([-5, -3.5, 0.8]) @ scale_matrix(0.2, 0.2, 0.8)
tree_crown = (translation_matrix([-5, -3.5, 2.4])
              @ rotation_matrix([1, 1, 1], np.radians(45))
              @ scale_matrix(0.9, 0.9, 0.9))

# Фигуры перечислены сзади вперёд: в этом порядке они и рисуются (см. ниже).
scene8 = [
    (tree_trunk @ vertices_cube, faces_cube, "saddlebrown"),
    (tree_crown @ vertices_cube, faces_cube, "forestgreen"),
] + transform_scene(house, M_house)

# Камера и перспектива для домика — те же шаги, что в заданиях 6 и 7.
camera8_position = np.array([13.0, -15.0, 7.0])
camera8_target = np.array([0.0, 0.0, 2.0])
Rc8 = camera_rotation(camera8_position, camera8_target)
C8 = translation_matrix(camera8_position) @ Rc8
C8_inv = inverse_camera(Rc8, camera8_position)

n8, f8 = 5.0, 45.0
polurazmer8 = n8 * np.tan(np.radians(40) / 2)
P8 = perspective_matrix(-polurazmer8, polurazmer8, -polurazmer8, polurazmer8, n8, f8)
print(f"C_8^-1 =\n{C8_inv}\n")
print(f"P_8 =\n{P8}\n")

depth8 = np.hstack(scene_vertices(transform_scene(scene8, C8_inv)))[2]
print(f"Глубина домика после C_8^-1: z от {depth8.min():.2f} до {depth8.max():.2f}\n")

# Matplotlib сортирует фигуры по глубине сам и прячет тонкие дверь и окна
# за стеной. Поэтому отключаем его сортировку: фигуры рисуются в порядке
# списка scene8, а грани внутри одной фигуры по-прежнему сортируются.
fig, ax = new_figure("Домик в мировых координатах", scene_vertices(scene8) + [C8[:, 3:]],
                     elev=35, azim=-15)
ax.computed_zorder = False
draw_scene(ax, scene8, alpha=1.0)
draw_camera(ax, C8, size=3.0)
save(fig, "p8_world")

scene8_persp = transform_scene(scene8, P8 @ C8_inv)
fig, ax = new_figure("Домик: камера и перспектива $P_8 C_8^{-1}$", scene_vertices(scene8_persp),
                     elev=-90, azim=0)
ax.computed_zorder = False
draw_scene(ax, scene8_persp, alpha=1.0)
ax.set_axis_off()
save(fig, "p8_render")
