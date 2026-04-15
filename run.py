#!/usr/bin/env python3
"""
AI Security Suite - Sistema de Defesa com IA
Versão Reescrita - Código Limpo e Organizado
"""

import os
import sys
import subprocess

def check_dependencies():
    missing = []
    try:
        import tkinter
    except ImportError:
        missing.append("python3-tk")
    
    if missing:
        print(f"\n⚠️ Faltando: {', '.join(missing)}")
        print("\nInstale: sudo apt-get install python3-tk")
        return False
    return True

def install_dependencies():
    print("\nInstalando dependências...")
    subprocess.run("sudo apt-get update", shell=True)
    subprocess.run("sudo apt-get install -y python3-tk ufw whois", shell=True)
    subprocess.run("pip3 install psutil scikit-learn --break-system-packages 2>/dev/null || pip3 install psutil scikit-learn --user", shell=True)

def main():
    print("=" * 50)
    print("  AI SECURITY SUITE - DEFESA TOTAL")
    print("=" * 50)
    
    if not check_dependencies():
        response = input("\nInstalar dependências? (s/N): ")
        if response.lower() == 's':
            install_dependencies()
        else:
            sys.exit(1)
    
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    try:
        from gui.main_window import MainWindow
        app = MainWindow()
        app.run()
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
