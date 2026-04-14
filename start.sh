#!/bin/bash
# Script de inicialização para Ubuntu/Linux Mint

echo "🛡️ Iniciando AI Security Suite..."

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    echo "⚠️ O programa precisa de permissões sudo para funcionar completamente"
    echo "Re-executando com sudo..."
    sudo python3 ~/ai-security-suite/run.py
else
    python3 ~/ai-security-suite/run.py
fi
