# Единый стиль графиков для всех отчётов курса.
# Использование:
#   import sys; sys.path.append('../../../template')
#   from plotstyle import setup, save
#   setup()
#   ... строим ...
#   save(fig, 'example')   # положит figures/example.pdf

import os
import matplotlib
import matplotlib.pyplot as plt

FIGURES_DIR = os.path.join(os.path.dirname(os.path.abspath('.')), 'figures')


def setup(font_size=11):
    # Шрифт без засечек читается на графиках лучше, размер согласован с текстом отчёта
    matplotlib.rcParams.update({
        'font.family': 'DejaVu Sans',
        'font.size': font_size,
        'axes.titlesize': font_size + 1,
        'axes.labelsize': font_size,
        'axes.grid': True,
        'grid.alpha': 0.3,
        'grid.linestyle': '--',
        'legend.frameon': True,
        'legend.framealpha': 0.9,
        'figure.figsize': (6.0, 4.0),
        'figure.dpi': 120,
        'savefig.dpi': 200,
        'savefig.bbox': 'tight',
        'lines.linewidth': 1.6,
        'axes.prop_cycle': matplotlib.cycler(color=[
            '#1f77b4', '#d62728', '#2ca02c', '#ff7f0e',
            '#9467bd', '#8c564b', '#17becf', '#7f7f7f',
        ]),
    })


def save(fig, name, figures_dir='../figures'):
    # PDF — вектор, в LaTeX вставляется без потери качества
    os.makedirs(figures_dir, exist_ok=True)
    path = os.path.join(figures_dir, f'{name}.pdf')
    fig.savefig(path)
    print(f'saved {path}')
    return path


def axes_2d(ax, lim=None, equal=True):
    # Оси через начало координат — так нагляднее для линейных отображений
    if equal:
        ax.set_aspect('equal', adjustable='box')
    if lim is not None:
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
    ax.axhline(0, color='black', linewidth=0.8, zorder=1)
    ax.axvline(0, color='black', linewidth=0.8, zorder=1)
    ax.set_xlabel('$x$')
    ax.set_ylabel('$y$')
    return ax


if __name__ == '__main__':
    import numpy as np
    setup()
    fig, ax = plt.subplots()
    t = np.linspace(0, 2 * np.pi, 200)
    ax.plot(np.cos(t), np.sin(t), label='единичная окружность')
    axes_2d(ax, lim=1.5)
    ax.legend()
    save(fig, 'example', figures_dir='.')
