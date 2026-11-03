"""Независимая проверка заданий 4–5; исходные файлы коллеги не изменяются.

python3 labs/lab03/verification/check_45.py
python3 labs/lab03/verification/check_45.py --report-text

Первый режим также сообщает опечатки в исходном черновике (код возврата 1).
Второй проверяет текст после явно заданных правок округления при сборке отчёта.
"""

import argparse
import contextlib
import importlib.util
import io
from pathlib import Path
import re
import runpy
import shutil
import tempfile

import matplotlib
matplotlib.use("Agg")
import numpy as np

LAB = Path(__file__).resolve().parents[1]


def rodrigues(v, theta):
    """Независимый расчёт без scipy.linalg.expm и функций проверяемого скрипта."""
    u = np.asarray(v, dtype=float) / np.linalg.norm(v)
    x, y, z = u
    K = np.array([[0, -z, y], [z, 0, -x], [-y, x, 0]])
    result = np.eye(4)
    result[:3, :3] = (np.cos(theta) * np.eye(3)
                     + (1 - np.cos(theta)) * np.outer(u, u) + np.sin(theta) * K)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-text", action="store_true")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="lab03-review45-") as tmp:
        script = Path(tmp) / "block_45.py"
        shutil.copy2(LAB / "block_45.py", script)
        with contextlib.redirect_stdout(io.StringIO()):
            block = runpy.run_path(str(script))
        assert len(list((Path(tmp) / "figures").glob("*.png"))) == 5

    V = block["vertices_cube"]
    R1 = rodrigues([1, 1, 0], np.pi / 2)
    R2 = rodrigues([0, 1, 1], np.pi / 3)
    pivot = np.array([1, 1, 1])
    P = R1.copy()
    P[:3, 3] = pivot - R1[:3, :3] @ pivot
    matrices = dict(R1=R1, R2=R2, M_1_then_2=R2 @ R1, M_2_then_1=R1 @ R2, M_pivot=P)
    distances = np.linalg.norm(V[:3, :, None] - V[:3, None, :], axis=0)
    for name, expected in matrices.items():
        matrix = block[name]
        np.testing.assert_allclose(matrix, expected, atol=1e-12, rtol=0)
        np.testing.assert_allclose(matrix[:3, :3].T @ matrix[:3, :3], np.eye(3), atol=1e-12)
        np.testing.assert_allclose(np.linalg.det(matrix[:3, :3]), 1, atol=1e-12)
        transformed = matrix @ V
        np.testing.assert_allclose(transformed[3], 1)
        np.testing.assert_allclose(np.linalg.norm(
            transformed[:3, :, None] - transformed[:3, None, :], axis=0), distances, atol=1e-12)
    for t in [-10, -1, 0, 1, 7]:
        point = np.r_[pivot + t * np.array([1, 1, 0]), 1]
        np.testing.assert_allclose(P @ point, point, atol=1e-12)
    assert not np.allclose(R2 @ R1, R1 @ R2)
    for matrix_name, axis_name in [("M_1_then_2", "axis_1_then_2"), ("M_2_then_1", "axis_2_then_1")]:
        axis = block[axis_name]
        np.testing.assert_allclose(block[matrix_name][:3, :3] @ axis, axis, atol=1e-12)
        np.testing.assert_allclose(np.linalg.norm(axis), 1, atol=1e-12)
    try:
        block["rotation_matrix"]([0, 0, 0], 1)
    except ValueError:
        pass
    else:
        raise AssertionError("Нулевая ось должна отклоняться")

    text = (LAB / "draft_45.md").read_text()
    if args.report_text:
        spec = importlib.util.spec_from_file_location("lab03_report", LAB / "report/build_report.py")
        report = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(report)
        text = report.prepare_teammate_draft(text)
    tables = re.findall(r"\| № вершины.*?(?=\n\n|\Z)", text, re.S)
    assert len(tables) == len(matrices)
    for (name, matrix), table in zip(matrices.items(), tables):
        rows = [[float(c.strip()) for c in line.strip("|").split("|")[1:]]
                for line in table.splitlines()[2:]]
        np.testing.assert_allclose(rows, (matrix @ V)[:3].T, atol=0.000500001, rtol=0)
    print("PASS: пять матриц, пять таблиц, сохранение расстояний, оси и неподвижные точки.")

    findings = []
    markers = ["Матрица первого поворота", "Матрица второго поворота",
               r"**Композиция $M_{1 \to 2} = R_2R_1$**",
               r"**Композиция $M_{2 \to 1} = R_1R_2$**", "После перемножения получаем"]
    for (name, expected), marker in zip(matrices.items(), markers):
        arrays = re.findall(r"\\begin\{bmatrix\}(.*?)\\end\{bmatrix\}", text[text.index(marker):], re.S)
        for body in arrays:
            if re.fullmatch(r"[\d.\s&\\-]+", body):
                printed = np.array([[float(c) for c in row.split("&")]
                                    for row in body.strip().split("\\\\")])
                if printed.shape == (4, 4):
                    break
        for row, col in np.argwhere(np.abs(printed - expected) > 0.000000500001):
            findings.append(f"{name}[{row + 1},{col + 1}]: {printed[row, col]:.6f} → {expected[row, col]:.6f}")
    for label, axis_name in [(r"u_{1 \to 2}", "axis_1_then_2"), (r"u_{2 \to 1}", "axis_2_then_1")]:
        body = re.search(re.escape(label) + r"\s*\\approx\s*\\begin\{bmatrix\}(.*?)\\end\{bmatrix\}", text, re.S)[1]
        printed = np.array([float(x) for x in body.strip().split("\\\\")])
        expected = block[axis_name]
        for index in np.flatnonzero(np.abs(printed - expected) > 0.0000500001):
            findings.append(f"{label}[{index + 1}]: {printed[index]:.4f} → {expected[index]:.4f}")
    for finding in findings:
        print("ROUNDING:", finding)
    print("Текст:", "сборочная версия" if args.report_text else "исходный черновик",
          f"— ошибок округления: {len(findings)}")
    return int(bool(findings))


if __name__ == "__main__":
    raise SystemExit(main())
