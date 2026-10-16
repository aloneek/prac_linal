#!/usr/bin/env bash
# Сборка отчёта: ./build.sh <номер лабы>, например ./build.sh 1
set -e
N=$(printf "%02d" "${1:?укажи номер лабы: ./build.sh 1}")
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/labs/lab$N/report"
xelatex -interaction=nonstopmode -halt-on-error report.tex >/dev/null
xelatex -interaction=nonstopmode -halt-on-error report.tex >/dev/null
echo "готово: labs/lab$N/report/report.pdf"
