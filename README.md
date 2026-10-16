# Практическая линейная алгебра — ИТМО, осень 2026

```
prac_linal/
├── CONTRIBUTING.md    как работать с репо втроём — начать отсюда
├── COURSE.md          правила зачёта, дедлайны, требования к отчёту
├── WORKFLOW.md        как мы работаем: роли, цикл работы над лабой, оформление
├── rules/             оригинальные сообщения преподавателя
├── lectures/          описания лекций со ссылками + доп. материал
├── tasks/             методички PLA_LAB1..6_2025.pdf
├── template/
│   ├── gostreport.sty оформление по ГОСТ 7.32 (XeLaTeX)
│   ├── report.tex     шаблон отчёта
│   ├── plotstyle.py   единый стиль графиков matplotlib
│   └── build.sh       сборка PDF: ./template/build.sh 1
└── labs/lab01..lab06/
    ├── README.md      чек-лист сдачи + контрольные вопросы + грабли
    ├── draft.md       черновик отчёта (пишу я)
    ├── code/          код
    ├── figures/       графики в PDF
    └── report/        report.tex → report.pdf
```

Сборка отчёта: `./template/build.sh 1`
Стиль графиков: `sys.path.append('../../../template'); from plotstyle import setup, save`
