#!/bin/bash
# Para o AI Security Suite

echo "🛑 Parando AI Security Suite..."

# Matar processos relacionados
sudo pkill -f "python3.*run.py"
sudo pkill -f "run.py"

sleep 1

if pgrep -f "python3.*run.py" > /dev/null; then
    echo "⚠️ Forçando encerramento..."
    sudo kill -9 $(pgrep -f "python3.*run.py") 2>/dev/null
fi

echo "✅ Programa encerrado!"
