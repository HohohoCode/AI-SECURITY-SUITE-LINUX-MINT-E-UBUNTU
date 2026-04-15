#!/bin/bash
# Inicia o AI Security Suite e garante que está no menu

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# ============================================
# VERIFICAR E ADICIONAR AO MENU SE NECESSÁRIO
# ============================================
MENU_FILE="$HOME/.local/share/applications/ai-security-suite.desktop"
ICON_FILE="$HOME/.local/share/icons/ai-security-suite.svg"

if [ ! -f "$MENU_FILE" ]; then
    echo "📌 Adicionando AI Security Suite ao menu..."
    
    # Criar diretório de ícones
    mkdir -p "$HOME/.local/share/icons"
    
    # Criar ícone
    cat > "$ICON_FILE" << 'ICONEOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
  <circle cx="50" cy="50" r="45" fill="#0f3460" stroke="#00d4ff" stroke-width="3"/>
  <path d="M50 20 L70 35 L70 55 L50 70 L30 55 L30 35 Z" fill="#00d4ff" opacity="0.8"/>
  <circle cx="50" cy="45" r="8" fill="#0a0e27"/>
  <rect x="45" y="55" width="10" height="15" fill="#0a0e27" rx="2"/>
  <text x="50" y="88" text-anchor="middle" fill="#00d4ff" font-size="8" font-weight="bold">AI</text>
</svg>
ICONEOF

    # Criar atalho no menu
    cat > "$MENU_FILE" << DESKTOPEOF
[Desktop Entry]
Version=1.0
Name=AI Security Suite
Comment=Sistema de Defesa com IA
Exec=$DIR/start_gui.sh
Icon=$ICON_FILE
Terminal=false
Type=Application
Categories=Security;System;
StartupNotify=true
DESKTOPEOF

    chmod +x "$MENU_FILE"
    update-desktop-database "$HOME/.local/share/applications/" 2>/dev/null
    echo "✅ Programa adicionado ao menu!"
fi

# ============================================
# INICIAR O PROGRAMA
# ============================================

# Verificar se zenity está instalado
if ! command -v zenity &> /dev/null; then
    echo "📦 Instalando zenity..."
    sudo apt-get install -y zenity
fi

# Pedir senha com janela gráfica
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
