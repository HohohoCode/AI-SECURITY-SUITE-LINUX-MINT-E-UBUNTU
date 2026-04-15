#!/bin/bash
# Inicia o AI Security Suite com janela gráfica - SEM TERMINAL

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Verificar se zenity está instalado
if ! command -v zenity &> /dev/null; then
    echo "Instalando zenity..."
    sudo apt-get install -y zenity
fi

# Pedir senha com zenity (janela gráfica)
PASSWORD=$(zenity --password --title="AI Security Suite" --text="Digite sua senha para iniciar o programa:")

if [ -z "$PASSWORD" ]; then
    zenity --error --text="Senha não fornecida." --timeout=2
    exit 1
fi

# Executar o programa
echo "$PASSWORD" | sudo -S python3 "$DIR/run.py" &

sleep 2

if pgrep -f "python3.*run.py" > /dev/null; then
    zenity --info --text="✅ AI Security Suite iniciado!" --timeout=2
else
    zenity --error --text="❌ Erro ao iniciar." --timeout=2
fi
