#!/bin/bash

echo "=========================================="
echo "  AI Security Suite - Instalação Universal"
echo "  (Linux Mint / Ubuntu / Debian)"
echo "=========================================="

# Detectar distribuição
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "📦 Distribuição detectada: $NAME $VERSION"
fi

# Instalar dependências do sistema
echo ""
echo "[1/4] Instalando dependências do sistema..."
sudo apt-get update
sudo apt-get install -y python3 python3-tk python3-pip ufw whois

# Instalar bibliotecas Python
echo ""
echo "[2/4] Instalando bibliotecas Python..."
pip3 install numpy pandas scikit-learn joblib pystray pillow --break-system-packages 2>/dev/null || pip3 install numpy pandas scikit-learn joblib pystray pillow --user

# Configurar firewall
echo ""
echo "[3/4] Configurando firewall..."
sudo ufw --force enable
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Criar atalho no menu
echo ""
echo "[4/4] Criando atalho no menu..."

# Para Ubuntu (GNOME)
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/ai-security-suite.desktop << DESKTOP
[Desktop Entry]
Version=1.0
Name=AI Security Suite
Comment=Sistema de Segurança com IA
Exec=sudo python3 $HOME/ai-security-suite/run.py
Icon=security-high
Terminal=false
Type=Application
Categories=Security;System;
StartupNotify=true
DESKTOP

# Para Linux Mint (Cinnamon)
if [ -d ~/.local/share/applications ]; then
    cp ~/.local/share/applications/ai-security-suite.desktop ~/.local/share/applications/
fi

echo ""
echo "=========================================="
echo "✅ INSTALAÇÃO CONCLUÍDA!"
echo "=========================================="
echo ""
echo "Para executar:"
echo "  sudo python3 ~/ai-security-suite/run.py"
echo ""
echo "Ou pelo menu: AI Security Suite"
echo ""
