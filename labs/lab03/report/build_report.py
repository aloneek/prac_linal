"""Собрать PDF блока A из draft.md, draft_A.md и данных block_a.py.

Запуск: python3 labs/lab03/report/build_report.py
Нужен XeLaTeX или Tectonic; путь можно передать через --engine.
"""

import argparse
import importlib.util
from pathlib import Path
import re
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
LAB = HERE.parent


def inline(text):
    """Оформить используемое в черновике подмножество Markdown, сохранив математику."""
    tokens = re.split(r"(\$[^$]+\$|`[^`]+`)", text)
    result = []
    for token in tokens:
        if token.startswith("$"):
            result.append(token)
            continue
        code = token.startswith("`")
        if code:
            token = token[1:-1]
        escapes = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%",
                   "_": r"\_", "#": r"\#", "{": r"\{", "}": r"\}"}
        token = "".join(escapes.get(c, c) for c in token)
        result.append(r"\texttt{" + token + "}" if code else token)
    return "".join(result)


FIGURES = {
    "p01_figures": (["cube", "tetra"], "Куб из методички и тетраэдр с выбранными вершинами"),
    "p02_scaling": (["s1", "s2", "s21"], "Два масштаба и их композиция"),
    "p03_translation": (["t1", "t2", "t21"], "Два переноса и их композиция; исходный куб показан контуром"),
    "p03_order": (["order"], "Сравнение порядка применения масштабирования и переноса"),
}


def figure(name):
    images, caption = FIGURES[name]
    out = [r"\begin{figure}[H]", r"\centering"]
    width = "0.83" if len(images) == 1 else "0.49"
    for i, image in enumerate(images):
        if i == 2:
            out.append(r"\par\medskip")
        out.append(r"\includegraphics[width=" + width + r"\linewidth]{figures/" + image + ".png}")
        if i == 0 and len(images) > 1:
            out.append(r"\hfill")
    out += [r"\caption{" + caption + "}", r"\label{fig:" + name + "}", r"\end{figure}"]
    return "\n".join(out)


def markdown(source):
    """Конвертер только форматов, используемых в черновике этого блока."""
    lines = source.splitlines()
    out, i, table_index, samepage = [], 0, 0, False
    while i < len(lines):
        line = lines[i]
        if line.strip() == "$$":
            i += 1
            math = []
            while i < len(lines) and lines[i].strip() != "$$":
                math.append(lines[i])
                i += 1
            if i == len(lines):
                raise ValueError("Незакрытая формула $$")
            out.append(r"\begin{center}\adjustbox{max width=\linewidth}{$\displaystyle "
                       + "\n".join(math) + r"$}\end{center}")
        elif line.startswith("```"):
            i += 1
            code = []
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            out.append("\\begin{lstlisting}[style=py,numbers=none]\n" + "\n".join(code) + "\n\\end{lstlisting}")
        elif line.startswith("## "):
            if samepage:
                out.append(r"\end{minipage}\par")
                samepage = False
            if line.startswith("## Задание 1."):
                out.append(r"\clearpage")
            out.append(r"\section{" + inline(line[3:]) + "}")
        elif line.startswith("### "):
            if line.startswith("### Вывод"):
                out.append(r"\par\noindent\begin{minipage}{\linewidth}")
                samepage = True
            out.append(r"\subsection*{" + inline(line[4:]) + "}")
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            if not re.fullmatch(r"[\s|:\-]+", "|".join(rows[1])):
                raise ValueError("Неподдерживаемая таблица Markdown")
            table_index += 1
            caption = ["Размеры куба после масштабирования", "Центры и размеры образов TS и ST"][table_index - 1]
            out += [r"\begin{table}[H]\centering", r"\caption{" + caption + "}",
                    r"\begin{adjustbox}{max width=\linewidth}",
                    r"\begin{tabular}{" + "l" * len(rows[0]) + "}", r"\toprule",
                    " & ".join(inline(c) for c in rows[0]) + r" \\", r"\midrule"]
            out += [" & ".join(inline(c) for c in row) + r" \\" for row in rows[2:]]
            out += [r"\bottomrule\end{tabular}\end{adjustbox}\end{table}"]
            continue
        elif line.startswith("!["):
            match = re.fullmatch(r"!\[.*\]\(figures/(\w+)\.png\)", line)
            if not match:
                raise ValueError(f"Неизвестный рисунок: {line}")
            out.append(figure(match[1]))
        else:
            converted = inline(line)
            for number, name in enumerate(FIGURES, 1):
                converted = re.sub(rf"(рисунк[ае])\s+{number}\b", rf"\1~\\ref{{fig:{name}}}", converted)
            out.append(converted)
        i += 1
    if samepage:
        out.append(r"\end{minipage}\par")
    return "\n".join(out)


def render_figures():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    spec = importlib.util.spec_from_file_location("lab03_block_a", LAB / "code/block_a.py")
    block = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(block)
    output = HERE / "figures"
    output.mkdir(exist_ok=True)
    with plt.rc_context({"font.size": 14, "axes.titlesize": 15}):
        transfers = [m @ block.vertices_cube for m in (block.T1, block.T2, block.T21)]
        cases = [
            ("cube", "Куб", block.vertices_cube, block.faces_cube),
            ("tetra", "Тетраэдр", block.vertices_tetra, block.faces_tetra),
            ("s1", "S₁: (2; 4; 10)", block.S1 @ block.vertices_cube, block.faces_cube),
            ("s2", "S₂: (0,5; 1; 0,1)", block.S2 @ block.vertices_cube, block.faces_cube),
            ("s21", "S₂S₁: (1; 4; 1)", block.S21 @ block.vertices_cube, block.faces_cube),
            ("t1", "T₁: (5; 5; 2)", transfers[0], block.faces_cube),
            ("t2", "T₂: (0; 3; 10)", transfers[1], block.faces_cube),
            ("t21", "T₂T₁: (5; 8; 12)", transfers[2], block.faces_cube),
        ]
        for name, title, vertices, faces in cases:
            fig = plt.figure(figsize=(6, 6), layout="constrained")
            ax = fig.add_subplot(projection="3d", proj_type="ortho")
            block.draw_shape(ax, vertices, faces, "blue")
            if name in {"t1", "t2", "t21"}:
                block.draw_shape(ax, block.vertices_cube, block.faces_cube, "none")
                block.set_scene_axes(ax, block.vertices_cube, *transfers)
            elif name in {"s1", "s2", "s21"}:
                extent = np.abs(vertices[:3]).max()
                block.set_scene_axes(ax, np.array([[-extent, extent]] * 3 + [[1, 1]]))
            else:
                block.set_scene_axes(ax, vertices)
            ax.set_title(title)
            fig.savefig(output / f"{name}.png", dpi=200)
            plt.close(fig)
        fig = block.plot_transform_order()
        for text in fig.axes[0].get_legend().get_texts():
            text.set_fontsize(12)
        fig.savefig(output / "order.png", dpi=200)
        plt.close(fig)


def build_source(font_dir=None):
    common = (LAB / "draft.md").read_text()
    data = re.search(r"## Исходные данные\n(.*?)(?=\n## )", common, re.S)[1]
    data = "\n".join(r"\item " + inline(line[2:]) if line.startswith("- ") else inline(line)
                     for line in data.strip().splitlines())
    draft = (LAB / "draft_A.md").read_text()
    draft = draft[draft.index("## Задание 1."):]
    font_config = ""
    if font_dir:
        directory = Path(font_dir).resolve()
        families = {
            "Liberation Serif": ["LiberationSerif-Regular.ttf", "LiberationSerif-Bold.ttf",
                                 "LiberationSerif-Italic.ttf", "LiberationSerif-BoldItalic.ttf"],
            "Liberation Sans": ["LiberationSans-Regular.ttf", "LiberationSans-Bold.ttf",
                                "LiberationSans-Italic.ttf", "LiberationSans-BoldItalic.ttf"],
            "DejaVu Sans Mono": ["DejaVuSansMono.ttf", "DejaVuSansMono-Bold.ttf",
                                 "DejaVuSansMono-Oblique.ttf", "DejaVuSansMono-BoldOblique.ttf"],
        }
        font_config = "\\usepackage{fontspec}\n"
        for family, files in families.items():
            for name in files:
                if not (directory / name).is_file():
                    raise FileNotFoundError(directory / name)
            keys = [f"Path={{{directory.as_posix()}/}}"]
            keys += [f"{key}={name}" for key, name in zip(
                ["UprightFont", "BoldFont", "ItalicFont", "BoldItalicFont"], files)]
            font_config += "\\defaultfontfeatures[" + family + "]{" + ",".join(keys) + "}\n"
        math_font = directory / "DejaVuMathTeXGyre.ttf"
        if not math_font.is_file():
            raise FileNotFoundError(math_font)
        # unicode-math также загружает шрифт напрямую для индексов: передаём имя файла.
        font_config += ("\\usepackage{amsmath,amssymb,mathtools}\n"
                        "\\usepackage{unicode-math}\n"
                        "\\let\\reportsetmathfont\\setmathfont\n"
                        "\\renewcommand{\\setmathfont}[1]{\\reportsetmathfont[Path={"
                        + directory.as_posix() + "/}]{DejaVuMathTeXGyre.ttf}}\n")
    source = r"""\documentclass[a4paper,14pt]{extarticle}
""" + font_config + r"""
\usepackage{../../../template/gostreport}
\ifdefined\reportsetmathfont\let\setmathfont\reportsetmathfont\fi
\usepackage{adjustbox}
\usepackage{etoolbox}
\usepackage{fvextra}
\patchcmd{\makegosttitle}{Выполнили:}{Выполнил:}{}{\errmessage{Не удалось оформить исполнителя}}
\hypersetup{pdftitle={ЛР3 — Матрицы в 3D-графике. Блок A: задания 1–3},pdfauthor={Осипов А. П.}}
\begin{document}
\makegosttitle{3}{Матрицы в 3D-графике}
{студент группы R3243 Осипов А.\,П.\\[8pt]
Блок A: задания 1--3}{Догадин Е.\,В.}
\tableofcontents
\clearpage
\unnumsection{Введение}
В отчёте представлен блок A лабораторной работы №3: отрисовка фигур
в однородных координатах, масштабирование и перенос куба, сравнение
порядка применения преобразований. Расчёты выполнены на Python с использованием
NumPy и Matplotlib. Все преобразования координат реализованы умножением на матрицы.
\unnumsection{Исходные данные}
\begin{itemize}
""" + data + "\n\\end{itemize}\n" + markdown(draft) + r"""
\unnumsection{Заключение по заданиям 1--3}
Однородные координаты позволяют задавать масштабирование и перенос матрицами
одного размера $4\times4$. Композиция выбранных масштабов восстанавливает
размеры по $x$ и $z$, сохраняя растяжение по $y$. Два переноса складываются,
а порядок переноса и масштабирования влияет на положение образа:
в $ST$ масштабируется и смещение. Равенство определителей $TS$ и $ST$
показывает одинаковое изменение объёма, но не равенство преобразований.
\clearpage
\unnumsection{Приложение А. Код блока A}
\begingroup\setstretch{0.95}
\VerbatimInput[breaklines,fontsize=\footnotesize,numbers=left,
numbersep=8pt,xleftmargin=14pt,frame=single]{../code/block_a.py}
\captionof{lstlisting}{Отрисовка фигур, масштабирование и перенос куба}
\endgroup
\end{document}
"""
    (HERE / "report.tex").write_text(source)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", help="Путь к xelatex или tectonic")
    parser.add_argument("--font-dir", help="Папка TTF-шрифтов, если они не установлены в системе")
    args = parser.parse_args()
    engine = args.engine or shutil.which("xelatex") or shutil.which("tectonic")
    if not engine:
        parser.error("Нужен XeLaTeX или Tectonic (--engine /путь/к/движку)")
    render_figures()
    build_source(args.font_dir)
    if "tectonic" in Path(engine).name:
        command = [engine, "--keep-logs", "--keep-intermediates", "report.tex"]
        subprocess.run(command, cwd=HERE, check=True)
    else:
        for _ in range(2):
            subprocess.run([engine, "-interaction=nonstopmode", "-halt-on-error", "report.tex"],
                           cwd=HERE, check=True)
    if not (HERE / "report.pdf").is_file():
        raise RuntimeError("TeX-движок не создал report.pdf")
    print(f"Готово: {HERE / 'report.pdf'}")


if __name__ == "__main__":
    main()
