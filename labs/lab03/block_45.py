"""ЛР3, задания 4-5. Вращение кубика вокруг оси и вокруг вершины.

Запуск: python block_45.py
Рисунки сохраняются в labs/lab03/figures/.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.linalg import expm

np.set_printoptions(precision=3, suppress=True)

FIGURES_DIR = Path(__file__).resolve().parent / "figures"

vertices_cube = np.array(
    [
        [-1, 1, 1, -1, -1, 1, 1, -1],
        [-1, -1, 1, 1, -1, -1, 1, 1],
        [-1, -1, -1, -1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
    ],
    dtype=float,
)

faces_cube = np.array(
    [
        [0, 1, 5, 4],
        [1, 2, 6, 5],
        [2, 3, 7, 6],
        [3, 0, 4, 7],
        [0, 1, 2, 3],
        [4, 5, 6, 7],
    ]
)


def normalize(v):
    """Возвращает единичный вектор, сонаправленный с v."""
    v = np.asarray(v, dtype=float)
    norm = np.linalg.norm(v)
    if np.isclose(norm, 0.0):
        raise ValueError("Нулевой вектор не может быть осью вращения.")
    return v / norm


def skew_matrix_4(u):
    """Кососимметрическая матрица 4x4 для нормированной оси u."""
    return np.array(
        [
            [0.0, -u[2], u[1], 0.0],
            [u[2], 0.0, -u[0], 0.0],
            [-u[1], u[0], 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0],
        ],
        dtype=float,
    )


def rotation_matrix(v, theta):
    """Матрица поворота R_v(theta) = exp(J * theta)."""
    u = normalize(v)
    return expm(theta * skew_matrix_4(u))


def translation_matrix(t):
    """Матрица переноса 4x4."""
    T = np.eye(4)
    T[:3, 3] = np.asarray(t, dtype=float)
    return T


def rotation_about_point(v, theta, point):
    """Вращение вокруг оси с направлением v, проходящей через точку point."""
    p = np.asarray(point, dtype=float)
    return translation_matrix(p) @ rotation_matrix(v, theta) @ translation_matrix(-p)


def rotation_axis_from_matrix(M):
    """Восстанавливает единичную ось вращения по матрице поворота 4x4."""
    R = M[:3, :3]
    axis = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]])
    norm = np.linalg.norm(axis)

    if norm < 1e-8:
        eigvals, eigvecs = np.linalg.eig(R)
        axis = np.real(eigvecs[:, np.argmin(np.abs(eigvals - 1.0))])
        norm = np.linalg.norm(axis)

    return axis / norm


def rotation_angle_from_matrix(M):
    """Угол поворота по следу матрицы, в градусах."""
    R = M[:3, :3]
    cosine = (np.trace(R) - 1.0) / 2.0
    return np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))


def draw_shape(ax, vertices, faces, color, label, alpha=1.0, zorder=1):
    """Рисует многогранник по однородным координатам вершин."""
    points = (vertices[:3, :] / vertices[3, :]).T
    collection = Poly3DCollection(
        points[faces],
        facecolors=color,
        edgecolors="k",
        linewidths=0.5,
        alpha=alpha,
        label=label,
        zorder=zorder,
    )
    ax.add_collection3d(collection)


def draw_axis(
    ax,
    direction,
    label,
    color="tab:green",
    length=2.0,
    zorder=10,
    origin=(0.0, 0.0, 0.0),
):
    """Рисует ось вращения: пунктирную прямую и вектор из начала координат."""
    u = normalize(direction)
    o = np.asarray(origin, dtype=float)

    ax.plot([], [], [], color=color, linestyle="--", label=label)
    ax.plot(
        [o[0] - length * u[0], o[0] + length * u[0]],
        [o[1] - length * u[1], o[1] + length * u[1]],
        [o[2] - length * u[2], o[2] + length * u[2]],
        color=color,
        linestyle="--",
        linewidth=2.0,
        zorder=zorder,
    )
    ax.quiver(
        o[0],
        o[1],
        o[2],
        length * u[0],
        length * u[1],
        length * u[2],
        color=color,
        arrow_length_ratio=0.08,
        zorder=zorder,
    )


def plot_case(
    name,
    title,
    V_old,
    V_new,
    faces,
    axis_direction,
    axis_label,
    axis_origin=(0.0, 0.0, 0.0),
):
    """Строит и сохраняет график: исходный кубик, повернутый кубик и ось."""
    fig = plt.figure(figsize=(6.5, 6.5))
    ax = fig.add_subplot(projection="3d")
    ax.computed_zorder = False

    draw_shape(ax, V_old, faces, "tab:blue", "Исходный кубик", alpha=0.18, zorder=1)
    draw_shape(ax, V_new, faces, "tab:red", "Повернутый кубик", alpha=0.55, zorder=2)
    draw_axis(ax, axis_direction, axis_label, zorder=10, origin=axis_origin)

    points_old = (V_old[:3, :] / V_old[3, :]).T
    points_new = (V_new[:3, :] / V_new[3, :]).T
    extent = np.max(np.abs(np.vstack([points_old, points_new])))
    limit = 2.0 if extent <= 2.0 else extent + 0.5
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_zlim(-limit, limit)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.set_title(title)
    ax.view_init(elev=25, azim=-60)
    ax.set_box_aspect([1, 1, 1])
    ax.legend(loc="upper left")

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / f"{name}.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"Сохранено: {path}")


def print_vertices(name, V):
    """Печатает декартовы координаты вершин после преобразования."""
    points = np.round((V[:3, :] / V[3, :]).T, 3)
    points[np.isclose(points, 0.0)] = 0.0
    print(f"Координаты после {name}:")
    print(points)
    print()


def check_rotation(name, M, axis):
    """Печатает проверки ортогональности, определителя и неподвижности оси."""
    R = M[:3, :3]
    p = np.append(normalize(axis), 1.0)
    print(f"{name}: det(R) = {np.linalg.det(R):.3f}")
    print(f"{name}: R^T R = I: {np.allclose(R.T @ R, np.eye(3))}")
    print(f"{name}: ось неподвижна: {np.allclose(M @ p, p)}")
    print()


def check_rotation_point(name, M, axis, point):
    """Проверки вращения вокруг оси, проходящей через заданную точку."""
    R = M[:3, :3]
    point = np.asarray(point, dtype=float)
    p = np.append(point, 1.0)
    d = np.append(normalize(axis), 0.0)
    expected_shift = point - R @ point
    print(f"{name}: det(R) = {np.linalg.det(R):.3f}")
    print(f"{name}: R^T R = I: {np.allclose(R.T @ R, np.eye(3))}")
    print(f"{name}: вершина {point} неподвижна: {np.allclose(M @ p, p)}")
    print(f"{name}: направление оси сохраняется: {np.allclose(M @ d, d)}")
    print(f"{name}: сдвиг M - R M: {np.allclose(M[:3, 3], expected_shift)}")
    print()


v1 = np.array([1.0, 1.0, 0.0])
theta1 = np.pi / 2.0

v2 = np.array([0.0, 1.0, 1.0])
theta2 = np.pi / 3.0

R1 = rotation_matrix(v1, theta1)
R2 = rotation_matrix(v2, theta2)

M_1_then_2 = R2 @ R1
M_2_then_1 = R1 @ R2

print("Матрица R1 = exp(J1 * theta1):")
print(R1)
print()
print("Матрица R2 = exp(J2 * theta2):")
print(R2)
print()

print("Матрица M_1_then_2 = R2 @ R1:")
print(M_1_then_2)
print()
print("Матрица M_2_then_1 = R1 @ R2:")
print(M_2_then_1)
print()

check_rotation("R1", R1, v1)
check_rotation("R2", R2, v2)

V1 = R1 @ vertices_cube
V2 = R2 @ vertices_cube
V_1_then_2 = M_1_then_2 @ vertices_cube
V_2_then_1 = M_2_then_1 @ vertices_cube

print_vertices("R1", V1)
print_vertices("R2", V2)
print_vertices("M_1_then_2 = R2 @ R1", V_1_then_2)
print_vertices("M_2_then_1 = R1 @ R2", V_2_then_1)

axis_1_then_2 = rotation_axis_from_matrix(M_1_then_2)
axis_2_then_1 = rotation_axis_from_matrix(M_2_then_1)

print("Ось вращения для M_1_then_2:", axis_1_then_2)
print("Ось вращения для M_2_then_1:", axis_2_then_1)
print("Угол M_1_then_2:", f"{rotation_angle_from_matrix(M_1_then_2):.2f}°")
print("Угол M_2_then_1:", f"{rotation_angle_from_matrix(M_2_then_1):.2f}°")
print()

check_rotation("M_1_then_2", M_1_then_2, axis_1_then_2)
check_rotation("M_2_then_1", M_2_then_1, axis_2_then_1)

plot_case(
    "p4A",
    r"Поворот вокруг оси $v_1 = (1, 1, 0)$, угол $90^\circ$",
    vertices_cube,
    V1,
    faces_cube,
    v1,
    "Ось $v_1$",
)
plot_case(
    "p4B",
    r"Поворот вокруг оси $v_2 = (0, 1, 1)$, угол $60^\circ$",
    vertices_cube,
    V2,
    faces_cube,
    v2,
    "Ось $v_2$",
)
plot_case(
    "p4AB",
    r"Композиция $M_{1 \to 2} = R_2 R_1$",
    vertices_cube,
    V_1_then_2,
    faces_cube,
    axis_1_then_2,
    r"Ось $M_{1 \to 2}$",
)
plot_case(
    "p4BA",
    r"Композиция $M_{2 \to 1} = R_1 R_2$",
    vertices_cube,
    V_2_then_1,
    faces_cube,
    axis_2_then_1,
    r"Ось $M_{2 \to 1}$",
)

vertex_index = 6
M_point = vertices_cube[:3, vertex_index]

v_pivot = np.array([1.0, 1.0, 0.0])
theta_pivot = np.pi / 2.0

M_pivot = rotation_about_point(v_pivot, theta_pivot, M_point)
V_pivot = M_pivot @ vertices_cube

print("Матрица M_pivot (вращение вокруг вершины):")
print(M_pivot)
print()

check_rotation_point("M_pivot", M_pivot, v_pivot, M_point)
print_vertices("M_pivot (вращение вокруг вершины)", V_pivot)
plot_case(
    "p5",
    r"Вращение вокруг вершины $M=(1,1,1)$, ось $v=(1,1,0)$, угол $90^\circ$",
    vertices_cube,
    V_pivot,
    faces_cube,
    v_pivot,
    r"Ось через вершину $M$",
    axis_origin=M_point,
)
