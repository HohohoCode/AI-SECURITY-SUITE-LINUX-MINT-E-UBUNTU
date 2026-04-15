#!/bin/bash
# Inicia o AI Security Suite com janela gráfica - SEM TERMINAL

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Pedir senha com zenity (janela gráfica)
PASSWORD=$(zenity --password --title="AI Security Suite" --text="Digite sua senha para iniciar o programa:")

# Verificar se o usuário cancelou
if [ -z "$PASSWORD" ]; then
    zenity --error --text="Senha não fornecida. Programa não iniciado." --timeout=2
    exit 1
fi

# Executar o programa com a senha fornecida
echo "$PASSWORD" | sudo -S python3 "$DIR/run.py" &

# Aguardar um pouco
sleep 2

# Verificar se iniciou
if pgrep -f "python3.*run.py" > /dev/null; then
    zenity --info --text="✅ AI Security Suite iniciado com sucesso!" --timeout=2
else
    zenity --error --text="❌ Erro ao iniciar o programa.\nVerifique sua senha." --timeout=3
fi
