"""Собрать общий PDF заданий 1–8 из черновиков и кода команды.

Запуск: python3 labs/lab03/report/build_report.py
Нужен XeLaTeX или Tectonic; путь можно передать через --engine.
"""

import argparse
import contextlib
import importlib.util
import io
from pathlib import Path
import re
import runpy
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
LAB = HERE.parent


def inline(text):
    """Оформить используемое в черновике подмножество Markdown, сохранив математику."""
    tokens = re.split(r"(\*\*.+?\*\*|\$[^$]+\$|`[^`]+`)", text)
    result = []
    for token in tokens:
        if token.startswith("**"):
            result.append(r"\textbf{" + inline(token[2:-2]) + "}")
            continue
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
    "p4A": (["p4A"], r"Поворот на $90^\circ$ вокруг оси $v_1=(1,1,0)$"),
    "p4B": (["p4B"], r"Поворот на $60^\circ$ вокруг оси $v_2=(0,1,1)$"),
    "p4AB": (["p4AB"], r"Композиция поворотов: сначала $R_1$, затем $R_2$"),
    "p4BA": (["p4BA"], r"Композиция поворотов: сначала $R_2$, затем $R_1$"),
    "p5": (["p5"], r"Поворот вокруг оси через вершину $M=(1,1,1)$"),
    "p6_views": (["p6_scene", "p6_bottom"], "Сцена из четырёх кубиков: стандартный ракурс и вид снизу"),
    "p6_camera": (["p6_camera"], r"Камера $C$, её оси и направление взгляда в мировых координатах"),
    "p6_inv": (["p6_inv", "p6_inv_bottom"], r"Сцена после $C^{-1}$: стандартный ракурс и вид камеры"),
    "p7_compare": (["p7_iso", "p7_persp"], r"Вид камеры: изометрия $C^{-1}$ и перспектива $PC^{-1}$"),
    "p7_deform1": (["p7_before1", "p7_after1"], r"Пространство до и после $P$, ракурс \texttt{view\_init(25, -60)}"),
    "p7_deform2": (["p7_before2", "p7_after2"], r"Пространство до и после $P$, ракурс \texttt{view\_init(10, -120)}"),
    "p8": (["p8_world", "p8_render"], "Домик из блоков: мировые координаты и кадр камеры с перспективой"),
}

FIGURES_68 = ["p6_scene", "p6_bottom", "p6_camera", "p6_inv", "p6_inv_bottom", "p7_iso", "p7_persp",
              "p7_before1", "p7_after1", "p7_before2", "p7_after2", "p8_world", "p8_render"]


def prepare_teammate_draft(source):
    """Учесть проверенные опечатки и добавить метки ссылок, сохранив исходник коллеги."""
    source = source.replace("0.376827", "0.376826").replace("0.0814", "0.0813")
    source = source.replace("Угол поворота определяется следом матрицы:",
                            "Угол поворота определяется следом верхнего левого блока $R$ размера $3\\times3$:")
    source = source.replace(
        "В развернутом виде матрица поворота вокруг произвольной оси, проходящей через начало координат, имеет вид",
        r"Для компактной записи положим $c=\cos\theta$, $s=\sin\theta$, $d=1-c$. "
        "Матрица поворота вокруг произвольной оси, проходящей через начало координат, имеет вид",
    )
    compact = r"""R_u(\theta) =
\begin{bmatrix}
c+u_x^2d & u_xu_yd-u_zs & u_xu_zd+u_ys & 0 \\
u_yu_xd+u_zs & c+u_y^2d & u_yu_zd-u_xs & 0 \\
u_zu_xd-u_ys & u_zu_yd+u_xs & c+u_z^2d & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}."""
    source = re.sub(r"R_u\(\\theta\) =\s*\\begin\{bmatrix\}.*?\\end\{bmatrix\}\.",
                    lambda _: compact, source, count=1, flags=re.S)
    def split_approximation(match):
        body = match[1]
        if body.count(r"\begin{bmatrix}") == 2 and body.count(r"\approx") == 1:
            exact, approximate = body.split(r"\approx", 1)
            return "$$\n\\begin{gathered}\n" + exact.strip() + r" \\[4pt]" + "\n\\approx " + approximate.strip() + "\n\\end{gathered}\n$$"
        return match[0]
    source = re.sub(r"\$\$\n(.*?)\n\$\$", split_approximation, source, flags=re.S)
    for number, name in enumerate(["p4A", "p4B", "p4AB", "p4BA"], 1):
        source = source.replace(
            f"Результат показан на рисунке, координаты вершин приведены в таблице 4.{number}.",
            f"Результат показан на рисунке {name}, координаты вершин приведены в таблице 4.{number}.",
        )
    source = source.replace("На рисунке показаны исходный кубик", "На рисунке p5 показаны исходный кубик")
    return source


def figure(name):
    images, caption = FIGURES[name]
    out = [r"\begin{figure}[H]", r"\centering"]
    width = "0.66" if name in {"p4A", "p4B", "p4AB", "p4BA", "p6_camera"} else "0.72" if name == "p5" else "0.83" if len(images) == 1 else "0.49"
    for i, image in enumerate(images):
        if i == 2:
            out.append(r"\par\medskip")
        out.append(r"\includegraphics[width=" + width + r"\linewidth]{figures/" + image + ".png}")
        if i == 0 and len(images) > 1:
            out.append(r"\hfill")
    out += [r"\caption{" + caption + "}", r"\label{fig:" + name + "}", r"\end{figure}"]
    return "\n".join(out)


def markdown(source, table_ids=None):
    """Конвертер только форматов, используемых в черновике этого блока."""
    lines = source.splitlines()
    out, i, table_index, samepage = [], 0, 0, False
    table_ids = table_ids or ["scale_sizes", "transform_order"]
    pending_caption = None
    task = None
    rotation_results = False
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
            task = int(re.match(r"## Задание (\d+)", line)[1])
            if task in {1, 4, 6}:
                out.append(r"\clearpage")
            out.append(r"\section{" + inline(line[3:]) + "}")
        elif line.startswith("### "):
            if line.startswith("### Вывод"):
                out.append(r"\par\noindent\begin{minipage}{\linewidth}")
                samepage = True
            out.append(r"\subsection*{" + inline(line[4:]) + "}")
        elif re.fullmatch(r"\*\*.*\*\*", line):
            heading = line[2:-2]
            if heading == "Результаты выполнения программы" and task == 4:
                rotation_results = True
            elif heading == "Анализ полученных результатов":
                rotation_results = False
            elif rotation_results and heading.startswith(("Поворот вокруг оси", "Композиция")):
                out.append(r"\clearpage")
            if heading.startswith("Таблица — "):
                pending_caption = heading.removeprefix("Таблица — ")
            elif heading == "Вывод":
                out += [r"\par\noindent\begin{minipage}{\linewidth}",
                        r"\subsection*{Вывод по заданию " + str(task) + "}"]
                samepage = True
            else:
                out.append(r"\subsection*{" + inline(heading) + "}")
        elif line.startswith("- "):
            out.append(r"\begin{itemize}")
            while i < len(lines) and lines[i].startswith("- "):
                out.append(r"\item " + inline(lines[i][2:]))
                i += 1
            out.append(r"\end{itemize}")
            continue
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            if not re.fullmatch(r"[\s|:\-]+", "|".join(rows[1])):
                raise ValueError("Неподдерживаемая таблица Markdown")
            table_index += 1
            caption = pending_caption or ["Размеры куба после масштабирования", "Центры и размеры образов TS и ST"][table_index - 1]
            pending_caption = None
            out += [r"\begin{table}[H]\centering\singlespacing\small", r"\caption{" + inline(caption) + "}",
                    r"\label{tab:" + table_ids[table_index - 1] + "}",
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
                # Имя в тексте уже экранировано inline(): p6_inv -> p6\_inv.
                label = re.escape(name.replace("_", r"\_"))
                converted = re.sub(rf"(рисунк[ае])\s+{label}\b", rf"\1~\\ref{{fig:{name}}}", converted)
            for number, name in enumerate(["p4A", "p4B", "p4AB", "p4BA"], 1):
                converted = re.sub(rf"(таблиц[ае])\s+4\.{number}\b", rf"\1~\\ref{{tab:{name}}}", converted)
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
        # Скрипт коллеги рисует графики при запуске. Изолируем его выходные файлы,
        # чтобы сборка не перезаписывала исходные figures/ из его коммита.
        with tempfile.TemporaryDirectory(prefix="lab03-45-") as tmp:
            script = Path(tmp) / "block_45.py"
            shutil.copy2(LAB / "block_45.py", script)
            with plt.rc_context({"font.size": 13, "figure.dpi": 180}), contextlib.redirect_stdout(io.StringIO()):
                runpy.run_path(str(script))
            for name in ["p4A", "p4B", "p4AB", "p4BA", "p5"]:
                shutil.copy2(Path(tmp) / "figures" / f"{name}.png", output / f"{name}.png")
        # block_68.py импортирует функции из code/block_a.py и block_45.py,
        # поэтому запускается на месте; его рисунки в figures/ перезаписываются им же.
        with plt.rc_context({"font.size": 13}), contextlib.redirect_stdout(io.StringIO()):
            runpy.run_path(str(LAB / "block_68.py"), run_name="__main__")
        for name in FIGURES_68:
            shutil.copy2(LAB / "figures" / f"{name}.png", output / f"{name}.png")


def build_source(font_dir=None):
    common = (LAB / "draft.md").read_text()
    data = re.search(r"## Исходные данные\n(.*?)(?=\n## )", common, re.S)[1]
    data = "\n".join(r"\item " + inline(line[2:]) if line.startswith("- ") else inline(line)
                     for line in data.strip().splitlines())
    draft = (LAB / "draft_A.md").read_text()
    draft = draft[draft.index("## Задание 1."):]
    draft45 = prepare_teammate_draft((LAB / "draft_45.md").read_text())
    draft68 = (LAB / "draft_68.md").read_text(encoding="utf-8")
    body = (markdown(draft) + "\n" + markdown(draft45, ["p4A", "p4B", "p4AB", "p4BA", "p5"])
            + "\n" + markdown(draft68, ["depth"]))
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
\hypersetup{pdftitle={ЛР3 — Матрицы в 3D-графике},pdfauthor={Осипов А. П.; Глазков В. Н.; Прохоревич И. Б.}}
\begin{document}
\makegosttitle{3}{Матрицы в 3D-графике}
{студент группы R3243 Осипов А.\,П.\\[4pt]
студент группы R3281 Глазков В.\,Н.\\[4pt]
студент группы R3235 Прохоревич И.\,Б.}{Догадин Е.\,В.}
\tableofcontents
\clearpage
\unnumsection{Введение}
В отчёте представлены задания 1--8 лабораторной работы №3: отрисовка фигур
в однородных координатах, масштабирование, перенос и вращение куба,
сравнение порядка применения преобразований, поворот вокруг оси через вершину,
матрица камеры, матрица перспективы и сцена-домик из блоков.
Расчёты выполнены на Python с использованием NumPy, Matplotlib и SciPy.
Все преобразования координат реализованы умножением на матрицы;
Matplotlib используется только как ортографический отрисовщик.
\unnumsection{Исходные данные}
\begin{itemize}
""" + data + "\n\\end{itemize}\n" + body + r"""
\clearpage
\unnumsection{Заключение}
Однородные координаты позволяют задавать масштабирование и перенос матрицами
одного размера $4\times4$. Композиция выбранных масштабов восстанавливает
размеры по $x$ и $z$, сохраняя растяжение по $y$. Два переноса складываются,
а порядок переноса и масштабирования влияет на положение образа:
в $ST$ масштабируется и смещение. Равенство определителей $TS$ и $ST$
показывает одинаковое изменение объёма, но не равенство преобразований.
Повороты, вычисленные с помощью матричной экспоненты,
сохраняют расстояния, углы и объём. Перестановка двух поворотов меняет
эквивалентную ось, хотя угол в рассмотренном случае совпадает.
Композиция $T(M)R_v(\theta)T(-M)$ позволяет вращать фигуру вокруг оси
через заданную точку, сохраняя точки этой оси неподвижными.
Матрица камеры $C=T_cR_c$ задаёт её положение и ориентацию, а обратная
$C^{-1}=R_c^TT(-\mathbf c)$ является движением: она записывает сцену
в системе координат камеры, не меняя формы объектов.
Матрица перспективы записывает глубину в четвёртую координату,
а деление на неё уменьшает дальние объекты. Пирамида видимости при этом
переходит в куб $[-1,1]^3$, кубы сцены — в усечённые пирамиды,
глубина сжимается нелинейно с сохранением порядка.
Цепочка $P\,C^{-1}M_{\text{model}}$ из произведений матриц $4\times4$
позволила собрать и отрисовать домик из блоков с камерой и перспективой.
\clearpage
\unnumsection{Приложение А. Код блока A}
\begingroup\setstretch{0.95}
\VerbatimInput[breaklines,fontsize=\footnotesize,numbers=left,
numbersep=8pt,xleftmargin=14pt,frame=single]{../code/block_a.py}
\captionof{lstlisting}{Отрисовка фигур, масштабирование и перенос куба}
\endgroup
\clearpage
\unnumsection{Приложение Б. Код заданий 4--5}
\begingroup\setstretch{0.95}
\VerbatimInput[breaklines,fontsize=\footnotesize,numbers=left,
numbersep=8pt,xleftmargin=14pt,frame=single]{../block_45.py}
\captionof{lstlisting}{Повороты вокруг оси через центр куба и через его вершину}
\endgroup
\clearpage
\unnumsection{Приложение В. Код заданий 6--8}
\begingroup\setstretch{0.95}
\VerbatimInput[breaklines,fontsize=\footnotesize,numbers=left,
numbersep=8pt,xleftmargin=14pt,frame=single]{../block_68.py}
\captionof{lstlisting}{Камера, перспектива и домик из блоков}
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
