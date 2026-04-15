#!/bin/bash
# Para o AI Security Suite

echo "🛑 Parando AI Security Suite..."
sudo pkill -f "python3.*run.py"
sudo pkill -f "run.py"
sleep 1
echo "✅ Programa encerrado!"
