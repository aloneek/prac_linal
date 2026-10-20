"""Сборка ЛР2: draft*.md -> report.tex -> report.pdf (через pandoc + xelatex).
Запуск: cd labs/lab02/report && python3 build_report.py
Перезапускать после каждой правки черновиков — всё пересобирается с нуля."""
import os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.dirname(HERE)

CAPTIONS = {  # подписи для картинок, которые в черновиках вставлены кодом, а не ![...]
    'p09': 'Пункт 9: образ многоугольника', 'p09c': 'Пункт 9: круг единичной площади и его образ',
    'p10': 'Пункт 10: образ многоугольника', 'p10c': 'Пункт 10: круг единичной площади и его образ',
    'p13': 'Пункт 13: отображение без вещественных собственных векторов',
    'p15A': 'Пункт 15: отображение $A$', 'p15B': 'Пункт 15: отображение $B$',
    'p15AB': 'Пункт 15: отображение $AB$', 'p15BA': 'Пункт 15: отображение $BA$',
    'p16A': 'Пункт 16: отображение $A$', 'p16B': 'Пункт 16: отображение $B$',
    'p16AB': 'Пункт 16: отображение $AB$', 'p16BA': 'Пункт 16: отображение $BA$',
}


def read(name):
    with open(os.path.join(LAB, name), encoding='utf-8') as f:
        return f.read()


def clean(md):
    md = re.sub(r'<!--.*?-->', '', md, flags=re.S)                # служебные комментарии
    md = '\n'.join(l for l in md.splitlines() if not l.startswith('>'))  # инструкции-цитаты
    md = re.sub(r'^# .*$', '', md, flags=re.M)                     # заголовки файлов
    md = re.sub(r'^\s*done\s*$', '', md, flags=re.M)
    md = re.sub(r'\n(!\[)', r'\n\n\1', md)                       # картинка — отдельным абзацем
    out, fence = [], False
    for l in md.splitlines():                                     # отступ 4+ пробела не должен
        if l.lstrip().startswith('```'):                          # превращаться в блок кода
            fence = not fence
        out.append(l if fence or l.lstrip().startswith(('-', '*', '|', '$')) else l.lstrip())
    md = '\n'.join(out)

    def code_to_figs(m):  # блок кода под «Визуализация» -> картинки по именам файлов
        names = re.findall(r'["\'](p\d+\w*)["\']', m.group(0))
        seen = []
        for n in names:
            if n not in seen and os.path.exists(os.path.join(LAB, 'figures', n + '.pdf')):
                seen.append(n)
        return '\n\n' + '\n\n'.join(f'![{CAPTIONS.get(n, n)}](figures/{n}.pdf)' for n in seen) + '\n\n'
    md = re.sub(r'```python.*?```', code_to_figs, md, flags=re.S)
    return md


def section(md, title):
    m = re.search(rf'^## {title}\s*\n(.*?)(?=^## |\Z)', md, flags=re.S | re.M)
    return m.group(1).strip() if m else ''


def item_key(block):
    m = re.match(r'## Пункт (\d+)', block)
    return int(m.group(1)) if m else 99


common = read('draft.md')
blocks = []
summary = ''
for f in ['draft_A.md', 'draft_B.md', 'draft_C.md']:
    md = clean(read(f))
    parts = re.split(r'(?=^## )', md, flags=re.M)
    for p in parts:
        p = p.strip()
        if p.startswith('## Пункт'):
            blocks.append(p)
        elif p.startswith('## '):
            summary += '\n\n' + re.sub(r'^## .*$', '', p, count=1, flags=re.M)
blocks.sort(key=item_key)

intro = section(clean(common), 'Введение')
data = section(clean(common), 'Исходные данные')
concl = section(clean(common), 'Заключение')

md = '# Исходные данные\n\n' + data + '\n\n'
md += '# Выполнение работы\n\n' + '\n\n'.join(blocks)
if summary.strip():
    md += '\n\n# Симметричность, инволютивность, ортогональность\n\n' + summary
md = md.replace('](figures/', '](../figures/')

tex = subprocess.run(['pandoc', '-f', 'markdown', '-t', 'latex', '--top-level-division=section'],
                     input=md, capture_output=True, text=True, check=True).stdout

# Рисунки: ГОСТ-вид, фиксированное место, метка fig:pNN
def fig(m):
    path, cap = m.group(1), m.group(2)
    name = os.path.splitext(os.path.basename(path))[0]
    return (f'\\begin{{figure}}[H]\n\\centering\n\\includegraphics[width=0.55\\textwidth]{{{path}}}\n'
            f'\\caption{{{cap}}}\n\\label{{fig:{name}}}\n\\end{{figure}}')
tex = re.sub(r'\\begin\{figure\}\s*\\centering\s*\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}\s*'
             r'\\caption\{(.*?)\}\s*\\end\{figure\}', fig, tex, flags=re.S)
# «на рисунке p01» -> «на рисунке 1» со ссылкой
tex = re.sub(r'(рисун\w*)\s+(p\d+\w*)', r'\1~\\ref{fig:\2}', tex)
tex = tex.replace('\\begin{longtable}[]', '\\begin{longtable}')
# широкие формулы ужимаем до ширины полосы (ГОСТ: ничего не вылезает за поля)
tex = re.sub(r'\\\[(.*?)\\\]', lambda m: '\\begin{center}\\adjustbox{max width=\\linewidth}{$\\displaystyle ' + m.group(1).strip() + '$}\\end{center}', tex, flags=re.S)
# сводная таблица: 5 колонок не влезают в l-колонки
tex = tex.replace('\\begin{longtable}{@{}lllll@{}}', '\\small\\begin{longtable}{@{}p{1.3cm}p{5.0cm}p{2.8cm}p{2.8cm}p{2.8cm}@{}}').replace('\\end{longtable}', '\\end{longtable}\\normalsize')

body_intro = intro or ('Цель работы --- изучить матрицы $2\\times 2$ как линейные отображения плоскости: '
                       'построить матрицы с заданными геометрическими свойствами, визуализировать их действие '
                       'на многоугольник и проанализировать ядро, образ, собственные числа и определители.')

doc = r'''\documentclass[a4paper,14pt]{extarticle}
\usepackage{../../../template/gostreport}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\usepackage{adjustbox}
\usepackage{hyperref}
\hypersetup{hidelinks}
\begin{document}
\makegosttitle
  {2}
  {2D-преобразования}
  {студент группы R3243 Осипов А.\,П.\\[4pt]
   студент группы R3243 Глазков В.\\[4pt]
   студент группы R3243 Прохоревич И.}
  {Догадин Е.\,В.}
\tableofcontents
\newpage
\unnumsection{Введение}
''' + body_intro + '\n\n' + tex + r'''

\unnumsection{Заключение}
''' + (concl or r'\textbf{TODO: заключение}') + r'''

\newpage
\unnumsection{Приложение А. Код}
\lstinputlisting[style=py,caption={Общий модуль \texttt{common.py}}]{../code/common.py}
\lstinputlisting[style=py,caption={Блок A: пункты 1--5}]{../code/block_a.py}
\lstinputlisting[style=py,caption={Блок B: пункты 6--8, 11, 12, 14}]{../code/block_b.py}
\lstinputlisting[style=py,caption={Блок C: пункты 9, 10, 13, 15, 16}]{../code/block_c.py}
\end{document}
'''
with open(os.path.join(HERE, 'report.tex'), 'w', encoding='utf-8') as f:
    f.write(doc)
for _ in range(2):
    r = subprocess.run(['xelatex', '-interaction=nonstopmode', 'report.tex'], cwd=HERE,
                       capture_output=True, text=True)
errs = [l for l in r.stdout.splitlines() if l.startswith('!')]
print('ошибки LaTeX:', errs[:10] if errs else 'нет')
print('готово:', os.path.join(HERE, 'report.pdf'))
