#!/usr/bin/env python3
"""
AI Security Suite - Sistema de Defesa com IA
"""

import os
import sys
import subprocess
import warnings

# Suprimir todos os warnings
warnings.filterwarnings('ignore')

# Configurar ambiente para evitar mensagens GDK
os.environ['GDK_BACKEND'] = 'x11'
os.environ['NO_AT_BRIDGE'] = '1'
os.environ['LIBGL_ALWAYS_SOFTWARE'] = '1'

# Redirecionar stderr para /dev/null para suprimir mensagens do GTK
sys.stderr = open(os.devnull, 'w')

def check_dependencies():
    missing = []
    try:
        import tkinter
    except ImportError:
        missing.append("python3-tk")
    
    if missing:
        sys.stderr = sys.__stderr__
        print(f"\n⚠️ Faltando: {', '.join(missing)}")
        print("\nInstale com: sudo apt-get install python3-tk")
        return False
    return True

def main():
    print("=" * 50)
    print("  AI SECURITY SUITE - DEFESA TOTAL")
    print("=" * 50)
    
    if not check_dependencies():
        sys.stderr = sys.__stderr__
        response = input("\nDeseja instalar as dependências? (s/N): ")
        if response.lower() == 's':
            subprocess.run("sudo apt-get update", shell=True)
            subprocess.run("sudo apt-get install -y python3-tk ufw whois", shell=True)
            subprocess.run("pip3 install psutil scikit-learn pystray pillow --break-system-packages 2>/dev/null", shell=True)
        else:
            sys.exit(1)
    
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    try:
        from gui.main_window import MainWindow
        app = MainWindow()
        app.run()
    except Exception as e:
        sys.stderr = sys.__stderr__
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
