#!/bin/bash
# Método mais confiável - pede senha no terminal mas fecha depois

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "🛡️ AI Security Suite"
echo ""

# Pedir senha (no terminal mesmo)
sudo -v

if [ $? -ne 0 ]; then
    echo "❌ Senha incorreta ou cancelada"
    exit 1
fi

echo ""
echo "🔐 Autenticado! Iniciando..."

# Executar em background e desassociar do terminal
(sudo python3 "$DIR/run.py" &) 2>/dev/null

# Aguardar um pouco
sleep 3

# Sair do terminal
exit 0
