"""ЛР3, блок A: задания 1–3, фигуры, масштабирование и перенос куба."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator
from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection


def draw_shape(ax, vertices, faces, color, *, alpha=1.0):
    """Нарисовать грани фигуры с вершинами в столбцах матрицы 4×N."""
    # Из (x, y, z, w) получаем декартовы координаты (x/w, y/w, z/w).
    points = (vertices[:3, :] / vertices[3, :]).T
    if color == "none":
        # Контур рисуем линиями: пустые грани Poly3DCollection поддерживаются не везде.
        contours = [points[np.r_[face, face[0]]] for face in faces]
        ax.add_collection3d(Line3DCollection(
            contours, colors="0.45", linewidths=0.8, linestyles="--"
        ))
        return
    ax.add_collection3d(
        Poly3DCollection(
            points[faces], facecolors=color, edgecolors="k", linewidths=0.2,
            alpha=alpha,
        )
    )


vertices_cube = np.array([
    [-1, 1, 1, -1, -1, 1, 1, -1],
    [-1, -1, 1, 1, -1, -1, 1, 1],
    [-1, -1, -1, -1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
])

faces_cube = np.array([
    [0, 1, 5, 4],
    [1, 2, 6, 5],
    [2, 3, 7, 6],
    [3, 0, 4, 7],
    [0, 1, 2, 3],
    [4, 5, 6, 7],
])

vertices_tetra = np.array([
    [-2,  4, 0,  1],  # x
    [-2, -4, 8,  1],  # y
    [ 0,  0, 0, 10],  # z
    [ 1,  1, 1,  1],  # w
])

faces_tetra = np.array([
    [0, 2, 1],  # основание
    [0, 1, 3],  # боковые грани
    [1, 2, 3],
    [2, 0, 3],
])

# Задание 2. Масштабы, выбранные Альбертом; четвёртая координата не меняется.
S1 = np.diag([2.0, 4.0, 10.0, 1.0])
S2 = np.diag([0.5, 1.0, 0.1, 1.0])
# Для векторов-столбцов сначала применяется правая матрица.
S21 = S2 @ S1

# Задание 3. Переносы, выбранные Альбертом, стоят в последнем столбце.
T1 = np.array([
    [1, 0, 0, 5],
    [0, 1, 0, 5],
    [0, 0, 1, 2],
    [0, 0, 0, 1],
], dtype=float)
T2 = np.array([
    [1, 0, 0, 0],
    [0, 1, 0, 3],
    [0, 0, 1, 10],
    [0, 0, 0, 1],
], dtype=float)
T21 = T2 @ T1
# Сравниваем первые выбранные матрицы переноса и масштаба.
TS = T1 @ S1
ST = S1 @ T1


def set_scene_axes(ax, *shapes):
    """Охватить все переданные фигуры, сохранив одинаковую единицу по осям."""
    points = np.hstack([vertices[:3, :] / vertices[3, :] for vertices in shapes])
    lower = points.min(axis=1)
    upper = points.max(axis=1)
    padding = 0.1 * (upper - lower)
    lower, upper = lower - padding, upper + padding
    ax.set_xlim(lower[0], upper[0])
    ax.set_ylim(lower[1], upper[1])
    ax.set_zlim(lower[2], upper[2])
    ax.set_box_aspect(upper - lower, zoom=0.85)
    ax.view_init(azim=-37.5, elev=30)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.set_major_locator(MaxNLocator(nbins=4))


def plot_translation():
    """Переносы и их композиция: исходный куб показан контуром."""
    fig = plt.figure(figsize=(15, 5), layout="constrained")
    fig.suptitle("Задание 3. Перенос куба (исходный — контур)")
    cases = [
        ("T₁: (5; 5; 2)", T1),
        ("T₂: (0; 3; 10)", T2),
        ("T₂T₁: (5; 8; 12)", T21),
    ]
    images = [matrix @ vertices_cube for _, matrix in cases]
    for i, ((title, matrix), transformed) in enumerate(zip(cases, images), start=1):
        ax = fig.add_subplot(1, 3, i, projection="3d", proj_type="ortho")
        draw_shape(ax, vertices_cube, faces_cube, "none")
        draw_shape(ax, transformed, faces_cube, "blue")
        # Одинаковые пределы для трёх панелей делают сдвиги сравнимыми.
        set_scene_axes(ax, vertices_cube, *images)
        ax.set_title(title)
        print(f"\n{title}\n{matrix}")
        print("Центр куба:", transformed[:3, :].mean(axis=1))
    return fig


def plot_transform_order():
    """Сравнить перенос после масштаба и масштаб после переноса."""
    fig = plt.figure(figsize=(8, 7), layout="constrained")
    ax = fig.add_subplot(projection="3d", proj_type="ortho")
    vertices_ts = TS @ vertices_cube
    vertices_st = ST @ vertices_cube
    draw_shape(ax, vertices_ts, faces_cube, "tab:blue", alpha=0.55)
    draw_shape(ax, vertices_st, faces_cube, "tab:orange", alpha=0.55)
    set_scene_axes(ax, vertices_ts, vertices_st)
    ax.set_title("Задание 3. Порядок преобразований: T = T₁, S = S₁")
    ax.legend(handles=[
        Patch(facecolor="tab:blue", alpha=0.55,
              label="TS: масштаб → перенос; центр (5; 5; 2)"),
        Patch(facecolor="tab:orange", alpha=0.55,
              label="ST: перенос → масштаб; центр (10; 20; 20)"),
    ], loc="upper left", fontsize=9)
    for name, matrix, transformed in [("TS", TS, vertices_ts), ("ST", ST, vertices_st)]:
        print(f"\n{name}\n{matrix}")
        print("Центр куба:", transformed[:3, :].mean(axis=1))
        print("Размеры по x, y, z:", np.ptp(transformed[:3, :], axis=1))
    return fig


def plot_scaling():
    """Три результата: каждый отдельный масштаб и их последовательное применение."""
    fig = plt.figure(figsize=(15, 5), layout="constrained")
    fig.suptitle("Задание 2. Масштабирование куба")

    cases = [
        ("S₁: (2; 4; 10)", S1),
        ("S₂: (0,5; 1; 0,1)", S2),
        ("S₂S₁: (1; 4; 1)", S21),
    ]
    for i, (title, matrix) in enumerate(cases, start=1):
        transformed = matrix @ vertices_cube
        ax = fig.add_subplot(1, 3, i, projection="3d", proj_type="ortho")
        draw_shape(ax, transformed, faces_cube, "blue")

        # Свои пределы для каждого рисунка, но единичный масштаб по осям одинаков.
        # Куб центрирован в начале; все его вершины должны попасть в область.
        extent = np.max(np.abs(transformed[:3, :] / transformed[3, :]))
        limit = 1.15 * extent
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
        ax.set_zlim(-limit, limit)
        ticks = np.linspace(-extent, extent, 5)
        ax.set_xticks(ticks)
        ax.set_yticks(ticks)
        ax.set_zticks(ticks)
        ax.set_box_aspect([1, 1, 1], zoom=0.85)
        ax.view_init(azim=-37.5, elev=30)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        ax.set_title(title)

        print(f"\n{title}\n{matrix}")
        print("Размеры по x, y, z:", np.ptp(transformed[:3, :], axis=1))
    return fig


def main():
    fig = plt.figure(figsize=(12, 6), layout="constrained")
    ax = fig.add_subplot(1, 2, 1, projection="3d", proj_type="ortho")

    draw_shape(ax, vertices_cube, faces_cube, "blue")

    ax.set_box_aspect([1, 1, 1], zoom=0.85)
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_zlim(-1, 1)
    ax.view_init(azim=-37.5, elev=30)

    ticks = np.linspace(-1, 1, 5)
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    ax.set_zticks(ticks)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.set_title("Куб из методички")

    ax_tetra = fig.add_subplot(1, 2, 2, projection="3d", proj_type="ortho")
    draw_shape(ax_tetra, vertices_tetra, faces_tetra, "blue")

    ax_tetra.set_xlim(-3, 5)
    ax_tetra.set_ylim(-5, 9)
    ax_tetra.set_zlim(-1, 11)
    # Диапазоны осей 8, 14, 12: единичный масштаб одинаков по всем осям.
    ax_tetra.set_box_aspect([8, 14, 12], zoom=0.85)
    ax_tetra.view_init(azim=-37.5, elev=30)
    ax_tetra.set_xlabel("x")
    ax_tetra.set_ylabel("y")
    ax_tetra.set_zlabel("z")
    ax_tetra.set_title("Тетраэдр Альберта")

    figures = {
        "p01_figures": fig,
        "p02_scaling": plot_scaling(),
        "p03_translation": plot_translation(),
        "p03_order": plot_transform_order(),
    }
    # Пути не зависят от рабочей папки: картинки черновика обновляются при запуске.
    figures_dir = Path(__file__).resolve().parents[1] / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    for name, figure in figures.items():
        path = figures_dir / f"{name}.png"
        figure.savefig(path, dpi=200)
        print(f"Сохранено: {path}")
    plt.show()


if __name__ == "__main__":
    main()
