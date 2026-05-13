#!/bin/bash
set -e

echo "========================================"
echo "  Android Lint — Auditoria de Acessibilidade"
echo "========================================"

cd /project

echo "[1/3] Executando gradle lintDebug..."
gradle lintDebug --no-daemon

REPORT_SRC="app/build/reports/lint-results-debug.html"

echo "[2/3] Copiando relatório para /reports..."
cp "${REPORT_SRC}" /reports/index.html

echo "[3/3] Concluído!"
echo ""
echo "  Relatório disponível em: http://localhost:8080"
echo "========================================"
