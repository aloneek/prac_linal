from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

C, D, K = 0.9, 1.1, 50
X0 = np.array([1.0, 0.0])
S = 1.0 / np.sqrt(2)
I2 = np.eye(2)
N = np.array([[1.0, -1.0], [1.0, -1.0]])
FIGURES_DIR = Path(__file__).resolve().parent / "figures"

CASES = [
    (1, -I2 + N),
    (2, S * np.array([[-1.0, -1.0], [1.0, -1.0]])),
    (3, np.array([[0.0, -1.0], [1.0, 0.0]])),
    (4, S * np.array([[1.0, -1.0], [1.0, 1.0]])),
    (5, I2 + N),
    (6, -C * I2 + N),
    (7, np.array([[0.0, -C], [C, 0.0]])),
    (8, C * I2 + N),
    (9, -D * I2 + N),
    (10, np.array([[0.0, -D], [D, 0.0]])),
    (11, D * I2 + N),
    (12, N.copy()),
]
STABLE = {1: np.array([1.0, 1.0]), 5: np.array([1.0, 1.0])}

FIGURES_DIR.mkdir(exist_ok=True)


def simulate(A, x0, kmax=K):
    X = np.zeros((kmax + 1, 2))
    X[0] = x0
    for k in range(kmax):
        X[k + 1] = A @ X[k]
    return X


def save(fig, name):
    fig.savefig(FIGURES_DIR / f"{name}.png", dpi=200)
    plt.close(fig)


def fmt_num(x, digits=3):
    if abs(x) < 1e-10:
        return "0"
    return f"{x:.{digits}g}"


def fmt_lambda(z):
    re, im = float(z.real), float(z.imag)
    eps = 1e-6
    if abs(im) < eps:
        return fmt_num(re)
    if abs(re) < eps:
        if abs(im - 1) < eps:
            return "i"
        if abs(im + 1) < eps:
            return "-i"
        return f"{fmt_num(im)}i"
    sign = "+" if im > 0 else "-"
    return f"{fmt_num(re)}{sign}{fmt_num(abs(im))}i"


def unique_eigenvalues(A, tol=1e-7):
    lam = np.linalg.eigvals(A)
    lam = np.where(np.abs(lam.imag) < 1e-6, lam.real + 0j, lam)
    values, counts = [], []
    for z in lam:
        for i, u in enumerate(values):
            if abs(z - u) < tol:
                counts[i] += 1
                break
        else:
            values.append(z)
            counts.append(1)
    order = sorted(range(len(values)), key=lambda i: (values[i].real, values[i].imag))
    return [(values[i], counts[i]) for i in order]


def plot_spectrum(n, A):
    eig = unique_eigenvalues(A)
    fig, ax = plt.subplots(figsize=(5.0, 5.0))
    t = np.linspace(0, 2 * np.pi, 400)
    ax.plot(np.cos(t), np.sin(t), "k--", lw=0.8, zorder=1)
    ax.axhline(0, color="gray", lw=0.5, zorder=0)
    ax.axvline(0, color="gray", lw=0.5, zorder=0)

    handles = [
        Line2D([0], [0], color="k", ls="--", lw=0.8, label="единичная окружность")
    ]
    for z, mult in eig:
        ax.plot(z.real, z.imag, "o", color="tab:red", ms=8, zorder=3)
        label = f"$\\lambda = {fmt_lambda(z)}$"
        if mult > 1:
            label += f" (кратность {mult})"
        handles.append(
            Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor="tab:red",
                ms=8,
                label=label,
            )
        )

    lim = max(1.35, float(np.max(np.abs(np.array([z for z, _ in eig])))) * 1.35)
    ax.set(
        xlim=(-lim, lim),
        ylim=(-lim, lim),
        xlabel=r"$\mathrm{Re}\,\lambda$",
        ylabel=r"$\mathrm{Im}\,\lambda$",
    )
    ax.set_aspect("equal")
    ax.legend(
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.14),
        ncol=2,
        fontsize=8,
        frameon=False,
    )
    save(fig, f"t2_{n:02d}_eig")


def plot_components(n, X):
    k = np.arange(len(X))
    for j, comp in [(0, "x1"), (1, "x2")]:
        fig, ax = plt.subplots(figsize=(7.2, 3.4))
        ax.stem(k, X[:, j], basefmt=" ")
        ax.axhline(0, color="gray", lw=0.5, zorder=0)
        ax.set(xlabel="$k$", ylabel=f"${comp[0]}_{comp[1]}(k)$")
        save(fig, f"t2_{n:02d}_{comp}")


def plot_phase(n, X):
    fig, ax = plt.subplots(figsize=(5.2, 5.2))
    ax.plot(X[:, 0], X[:, 1], "o-", ms=3, lw=0.9, label="траектория")
    ax.plot(X[0, 0], X[0, 1], "s", color="tab:green", ms=7, label="$x(0)$", zorder=3)
    ax.plot(0, 0, "k+", ms=9, label="начало координат", zorder=3)
    ax.set(xlabel="$x_1$", ylabel="$x_2$")
    ax.set_aspect("equal")
    ax.legend(fontsize=8)
    save(fig, f"t2_{n:02d}_phase")


def plot_stable(n, A, x0):
    X = simulate(A, x0)
    k = np.arange(len(X))
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.stem(k, X[:, 0], basefmt=" ", label="$x_1(k)$")
    ax.plot(k, X[:, 1], "x", color="tab:red", ms=7, label="$x_2(k)$")
    ax.axhline(0, color="gray", lw=0.5, zorder=0)
    ax.set(xlabel="$k$", ylabel="$x_1(k),\\ x_2(k)$")
    handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor="tab:blue",
            ms=7,
            linestyle="none",
            label="$x_1(k)$",
        ),
        Line2D(
            [0],
            [0],
            marker="x",
            color="tab:red",
            ms=7,
            linestyle="none",
            label="$x_2(k)$",
        ),
    ]
    ax.legend(
        handles=handles,
        fontsize=8,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.18),
        ncol=2,
        frameon=False,
    )
    save(fig, f"t2_{n:02d}_stable")


print(f"{'№':>2} {'x(50)':>26} {'||x(50)||':>12} {'max||x||':>10} {'k_max':>6}")
for n, A in CASES:
    X = simulate(A, X0)
    plot_spectrum(n, A)
    plot_components(n, X)
    plot_phase(n, X)
    if n in STABLE:
        plot_stable(n, A, STABLE[n])
    nrm = np.linalg.norm(X, axis=1)
    print(
        f"{n:>2} {str(np.round(X[-1], 4)):>26} {nrm[-1]:>12.4g} {nrm.max():>10.4g} {int(nrm.argmax()):>6}"
    )
