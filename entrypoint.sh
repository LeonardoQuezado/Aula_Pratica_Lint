#!/bin/bash
set -e

echo "========================================"
echo "  Android Lint — Auditoria de Acessibilidade"
echo "========================================"

cd /project

echo "[1/3] Executando gradle lintDebug..."
gradle lintDebug --no-daemon

XML_REPORT="app/build/reports/lint-results-debug.xml"

echo "[2/3] Gerando dashboard customizado..."
python3 /generate_dashboard.py "${XML_REPORT}" /reports/index.html

echo "[3/3] Concluído!"
echo ""
echo "  Relatório disponível em: http://localhost:8080"
echo "========================================"
