"""ЛР4, задание 3: маятник около нижнего и верхнего равновесия.

Запуск из любой папки: python3 labs/lab04/code/task3.py
Зависимости: numpy, matplotlib. Данные сохраняются рядом с графиками.
"""
from dataclasses import dataclass
from pathlib import Path
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "template"))
from plotstyle import setup, save

LAB = Path(__file__).resolve().parents[1]
FIGURES = LAB / "figures"
# Угол в радианах, угловая скорость в радианах в секунду.
INITIAL = np.array([[.08, 0], [0, .16], [-.08, .08], [.08, -.16], [.04, -.16]])


@dataclass(frozen=True)
class Case:
    key: str
    a: float
    b: float
    duration: float
    title: str
    stable_lambda: float | None = None

    @property
    def matrix(self):
        return np.array([[0., 1.], [self.a, self.b]])


CASES = (
    Case("t3_1", -4, 0, 8, "Нижнее равновесие без трения: центр"),
    Case("t3_2", -4, -2, 8, "Нижнее равновесие с трением: устойчивый фокус"),
    Case("t3_3", 4, 0, 2, "Верхнее равновесие без трения: седло", -2),
    Case("t3_4", 4, -3, 2, "Верхнее равновесие с трением: седло", -4),
    Case("t3_2c", -4, -4, 8, "Критическое затухание: вырожденный узел"),
    Case("t3_2o", -4, -5, 8, "Сильное затухание: устойчивый узел"),
)


def fundamental(a, b, t):
    """Вещественная exp(At) без диагонализации; работает и для жордановой клетки.

    A = hI + B, B² = (a + b²/4)I. При кратном корне
    используется точная предельная формула exp(ht)(I+tB).
    """
    t = np.asarray(t, dtype=float)
    h = b / 2
    B = np.array([[-h, 1.], [a, h]])
    delta = a + h * h
    if delta == 0.:
        c, s = np.ones_like(t), t
    elif delta < 0:
        w = np.sqrt(-delta)
        c, s = np.cos(w*t), np.sin(w*t)/w
    else:
        w = np.sqrt(delta)
        c, s = np.cosh(w*t), np.sinh(w*t)/w
    return np.exp(h*t)[..., None, None] * (
        c[..., None, None] * np.eye(2) + s[..., None, None] * B)


def trajectories(case, t, initial=INITIAL):
    return np.einsum("tij,nj->nti", fundamental(case.a, case.b, t), initial)


def label(x):
    return f"({x[0]:.2f}; {x[1]:.2f})"


def plot_triplet(case, t, initial, values, suffix=""):
    """Отдельные x1(t), x2(t), фазовый портрет; единые цвета начальных условий."""
    phase = []
    for component in (0, 1, None):
        fig, ax = plt.subplots(figsize=(6.7, 3.8), layout="constrained")
        for n, (x0, x) in enumerate(zip(initial, values)):
            if component is None:
                line, = ax.plot(x[:, 0], x[:, 1], label=label(x0))
                ax.plot(*x[0], "o", color=line.get_color(), ms=4)
                j = len(t) // 3
                ax.annotate("", xy=x[j+5], xytext=x[j],
                            arrowprops={"arrowstyle": "->", "color": line.get_color()})
            else:
                ax.plot(t, x[:, component], label=label(x0))
        ax.axhline(0, color="black", lw=.6)
        if component is None:
            ax.axvline(0, color="black", lw=.6)
            ax.set_xlabel(r"$x_1=\theta$, рад")
            ax.set_ylabel(r"$x_2=\dot\theta$, рад/с")
            # Разные размерности координат: одинаковый масштаб осей не требуется.
            if not suffix and case.stable_lambda is not None:
                xx = np.linspace(*ax.get_xlim(), 100)
                ax.plot(xx, case.stable_lambda*xx, "k--", lw=1,
                        label="Устойчивая прямая")
        else:
            ax.set_xlabel("Время t, с")
            ax.set_ylabel((r"$x_1=\theta$, рад" if component == 0
                           else r"$x_2=\dot\theta$, рад/с"))
        ax.set_title(case.title + ("\nУстойчивые траектории" if suffix else ""), fontsize=10)
        ax.legend(title=r"$x(0)=(x_1; x_2)$", fontsize=8, title_fontsize=9,
                  loc="best", ncol=2 if len(initial) > 3 else 1)
        name = case.key + suffix + ("_phase" if component is None else f"_x{component+1}")
        save(fig, name, figures_dir=str(FIGURES))
        # PNG нужен для быстрого просмотра без PDF-редактора.
        fig.savefig(FIGURES / f"{name}.png", dpi=150)
        plt.close(fig)
        phase.append(name)
    return phase


def main():
    setup()
    FIGURES.mkdir(parents=True, exist_ok=True)
    results = {}
    for case in CASES:
        t = np.linspace(0, case.duration, 1601)
        values = trajectories(case, t)
        names = plot_triplet(case, t, INITIAL, values)
        np.savez(FIGURES / f"{case.key}_data.npz", t=t, initial=INITIAL, x=values)
        roots = np.roots([1, -case.b, -case.a]).astype(complex)
        result = {"a": case.a, "b": case.b, "A": case.matrix.tolist(),
                  "eigenvalues": [[z.real, z.imag] for z in roots],
                  "initial": INITIAL.tolist(), "figures": names,
                  "max_abs_angle": float(np.abs(values[:, :, 0]).max())}
        if case.stable_lambda is not None:
            # Аналитическое вычисление устойчивой ветви исключает примесь
            # растущей моды от округления при длительном расчёте exp(At)x0.
            lam = case.stable_lambda
            initial = np.array([[.08, .08*lam], [-.08, -.08*lam]])
            ts = np.linspace(0, 4, 1601)
            xs = np.exp(lam*ts)[None, :, None]*initial[:, None, :]
            result["stable_figures"] = plot_triplet(case, ts, initial, xs, "_stable")
            result["stable_initial"] = initial.tolist()
        results[case.key] = result
    (FIGURES / "t3_results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Задание 3: расчёты и графики сохранены.")


if __name__ == "__main__":
    main()
