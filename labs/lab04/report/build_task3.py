"""Сборка отдельного отчёта по заданию 3 и LaTeX-раздела для общего PDF.

python3 labs/lab04/report/build_task3.py --engine /путь/к/tectonic
Графики предварительно создаются code/task3.py. Поддерживается XeLaTeX.
"""
import argparse
from pathlib import Path
import re
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
LAB = HERE.parent


def inline(text):
    pieces = re.split(r'(\$[^$]+\$|\*\*.+?\*\*|`[^`]+`)', text)
    out = []
    for piece in pieces:
        if piece.startswith('$'):
            out.append(piece)
        elif piece.startswith('**'):
            out.append(r'\textbf{' + inline(piece[2:-2]) + '}')
        else:
            code = piece.startswith('`')
            if code:
                piece = piece[1:-1]
            escapes = {'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%',
                       '_': r'\_', '#': r'\#', '{': r'\{', '}': r'\}'}
            piece = ''.join(escapes.get(c, c) for c in piece)
            out.append(r'\texttt{' + piece + '}' if code else piece)
    return ''.join(out)


def convert(source):
    out, math = [], False
    figure_names = re.findall(r'\]\(figures/(\w+)\.pdf\)', source)
    for line in source.splitlines():
        if line.strip() == '$$':
            out.append(r'\end{equation}' if math else r'\begin{equation}')
            math = not math
        elif math:
            out.append(line)
        elif line.startswith('# '):
            out.append(r'\section{' + inline(line[2:]) + '}')
        elif line.startswith('## '):
            out.append(r'\subsection{' + inline(line[3:]) + '}')
        elif line.startswith('### '):
            out.append(r'\subsubsection{' + inline(line[4:]) + '}')
        elif line.startswith('!['):
            caption, name = re.fullmatch(r'!\[(.*)\]\(figures/(\w+)\.pdf\)', line).groups()
            out.append(r'\begin{figure}[H]\centering' + '\n' +
                       r'\includegraphics[width=0.82\linewidth]{../figures/' + name + '.pdf}\n' +
                       r'\caption{' + inline(caption) + r'}\label{fig:' + name + '}\n' +
                       r'\end{figure}')
        else:
            # Вначале выделяем идентификаторы рисунков; они не попадут в inline().
            parts = re.split('(' + '|'.join(sorted(figure_names, key=len, reverse=True)) + ')', line)
            out.append(''.join(r'\ref{fig:' + p + '}' if p in figure_names else inline(p)
                               for p in parts))
    if math:
        raise ValueError('Незакрытая формула')
    return '\n'.join(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine')
    args = parser.parse_args()
    engine = args.engine or shutil.which('xelatex') or shutil.which('tectonic')
    body = convert((LAB / 'draft_task3.md').read_text(encoding='utf-8'))
    (HERE / 'section_task3.tex').write_text(body + '\n', encoding='utf-8')
    # На macOS доступны Times New Roman и Arial; в Linux — Liberation.
    mac = Path('/System/Library/Fonts/Supplemental/Times New Roman.ttf').exists()
    serif, sans, mono = (('Times New Roman', 'Arial', 'Menlo') if mac else
                          ('Liberation Serif', 'Liberation Sans', 'DejaVu Sans Mono'))
    preamble = r'''\documentclass[a4paper,14pt]{extarticle}
\usepackage{fontspec}
\usepackage{polyglossia}
\setmainlanguage{russian}
\setmainfont{SERIF}
\setsansfont{SANS}
\setmonofont{MONO}[Scale=0.75]
\usepackage{amsmath,amssymb,graphicx,float}
\usepackage[a4paper,left=30mm,right=15mm,top=20mm,bottom=20mm]{geometry}
\usepackage{setspace}
\onehalfspacing
\setlength{\parindent}{1.25cm}
\emergencystretch=3em
\usepackage{caption}
\captionsetup{labelsep=endash,justification=centering}
\addto\captionsrussian{\renewcommand{\figurename}{Рисунок}}
\usepackage[unicode,hidelinks]{hyperref}
\usepackage{fvextra}
\setcounter{tocdepth}{2}
\hypersetup{pdftitle={ЛР4. Задание 3. Осциллятор},pdfauthor={Осипов А. П.}}
\begin{document}
\begin{titlepage}
\centering
Университет ИТМО\\
Практическая линейная алгебра
\vfill
{\Large\bfseries Лабораторная работа №4\\[8pt] Динамические системы}\\[20pt]
{\large Задание 3. Осциллятор}\\[12pt]
Отдельная часть для включения в командный отчёт
\vfill
\begin{flushright}
Выполнил: Осипов А.\,П.\\
Преподаватель: Догадин Е.\,В.
\end{flushright}
\vfill
Санкт-Петербург, 2026
\end{titlepage}
\tableofcontents
\clearpage
'''.replace('SERIF', serif).replace('SANS', sans).replace('MONO', mono)
    source = preamble + body + r'''
\clearpage
\section*{Приложение А. Программа моделирования}
\addcontentsline{toc}{section}{Приложение А. Программа моделирования}
\VerbatimInput[breaklines=true,fontsize=\small,numbers=left,numbersep=5pt]{../code/task3.py}
\end{document}
'''
    (HERE / 'task3.tex').write_text(source, encoding='utf-8')
    if not engine:
        parser.error('LaTeX создан. Для PDF укажите --engine с путём к XeLaTeX или Tectonic.')
    if 'tectonic' in Path(engine).name:
        subprocess.run([engine, '--keep-logs', 'task3.tex'], cwd=HERE, check=True)
    else:
        for _ in range(2):
            subprocess.run([engine, '-interaction=nonstopmode', '-halt-on-error', 'task3.tex'],
                           cwd=HERE, check=True)
    print(HERE / 'task3.pdf')


if __name__ == '__main__':
    main()
