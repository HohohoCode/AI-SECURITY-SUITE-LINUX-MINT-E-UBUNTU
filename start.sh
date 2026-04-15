#!/bin/bash
# Inicia o AI Security Suite (com janela normal)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "🛡️ Iniciando AI Security Suite..."
sudo python3 "$DIR/run.py"
