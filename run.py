#!/usr/bin/env python3
import os
import sys
import subprocess

def check_dependencies():
    """Verifica dependências"""
    missing = []
    
    # Verificar tkinter
    try:
        import tkinter
    except ImportError:
        missing.append("python3-tk")
    
    # Verificar numpy (opcional)
    try:
        import numpy
    except ImportError:
        missing.append("numpy (opcional)")
    
    if missing:
        print(f"\n⚠️ Dependências faltando: {', '.join(missing)}")
        print("\nInstale com:")
        print("  sudo apt-get install python3-tk")
        print("  pip3 install numpy pandas scikit-learn")
        return False
    
    return True

def install_dependencies():
    """Instala dependências automaticamente"""
    print("\nInstalando dependências...")
    subprocess.run("sudo apt-get update", shell=True)
    subprocess.run("sudo apt-get install -y python3-tk ufw whois", shell=True)
    subprocess.run("pip3 install numpy pandas scikit-learn joblib pystray pillow --break-system-packages 2>/dev/null || pip3 install numpy pandas scikit-learn joblib pystray pillow --user", shell=True)
    print("✅ Dependências instaladas!")

def main():
    print("=" * 50)
    print("  AI Security Suite - Linux (Ubuntu/Mint)")
    print("=" * 50)
    
    if not check_dependencies():
        response = input("\nDeseja instalar as dependências? (s/N): ")
        if response.lower() == 's':
            install_dependencies()
        else:
            print("Instalação cancelada.")
            sys.exit(1)
    
    # Adicionar ao path
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
