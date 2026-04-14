import tkinter as tk
import threading
import time
from datetime import datetime
import os

# Tentar importar bibliotecas do system tray
try:
    import pystray
    from PIL import Image, ImageDraw
    SYSTEM_TRAY_AVAILABLE = True
except ImportError:
    SYSTEM_TRAY_AVAILABLE = False
    print("⚠️ pystray não disponível. Instale com: pip3 install pystray pillow")

from src.config.settings import Settings
from src.core.defense_engine import DefenseEngine
from src.core.counter_attack import CounterAttack
from src.gui.dashboard_tab import DashboardTab
from src.gui.threats_tab import ThreatsTab
from src.gui.firewall_tab import FirewallTab
from src.gui.counter_tab import CounterTab
from src.gui.logs_tab import LogsTab
from src.gui.settings_tab import SettingsTab
from src.gui.ai_tab import AITab

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🛡️ AI Security Suite - IA Real")
        self.root.geometry("1400x850")
        self.root.configure(bg='#0a0a1a')
        self.root.minsize(1200, 700)
        
        self.settings = Settings()
        self.defense_engine = DefenseEngine(self.settings, self.handle_event)
        self.counter_attack = CounterAttack(self.settings, self.handle_event)
        self.is_defense_active = False
        self.tray_icon = None
        self.is_minimized = False
        
        self.setup_ui()
        self.start_updates()
        self.setup_tray_icon()
        
        # Configurar evento de fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg='#0f3460', height=70)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text="🛡️ AI SECURITY SUITE", font=('Arial', 20, 'bold'),
                bg='#0f3460', fg='#00ff88').pack(side='left', padx=30)
        
        # Badge IA
        tk.Label(header, text="🧠 IA REAL | Isolation Forest + Random Forest", 
                bg='#ff8800', fg='#0a0a1a', font=('Arial', 9, 'bold'), padx=10, pady=3).pack(side='left', padx=10)
        
        # Botão de minimizar para systray
        self.tray_btn = tk.Button(header, text="📌", command=self.minimize_to_tray,
                                  bg='#0f3460', fg='#00ff88', font=('Arial', 14, 'bold'),
                                  padx=10, pady=5, cursor='hand2', relief='flat')
        self.tray_btn.pack(side='right', padx=5)
        
        # Botão de minimizar normal
        self.minimize_btn = tk.Button(header, text="─", command=self.minimize_window,
                                      bg='#0f3460', fg='#00ff88', font=('Arial', 14, 'bold'),
                                      padx=10, pady=5, cursor='hand2', relief='flat')
        self.minimize_btn.pack(side='right', padx=2)
        
        # Interruptor da defesa
        self.defense_switch_canvas = tk.Canvas(header, width=60, height=30, bg='#0f3460', highlightthickness=0)
        self.defense_switch_canvas.pack(side='right', padx=30)
        self.defense_switch_bg = self.defense_switch_canvas.create_rectangle(3, 3, 57, 27, fill='#555', outline='')
        self.defense_switch_btn = self.defense_switch_canvas.create_oval(5, 5, 25, 25, fill='white', outline='')
        self.defense_switch_text = self.defense_switch_canvas.create_text(42, 15, text="OFF", fill='white', font=('Arial', 9, 'bold'))
        self.defense_switch_canvas.tag_bind(self.defense_switch_bg, '<Button-1>', self.toggle_defense)
        self.defense_switch_canvas.tag_bind(self.defense_switch_btn, '<Button-1>', self.toggle_defense)
        
        self.defense_status_label = tk.Label(header, text="DEFESA: INATIVA", bg='#0f3460', fg='#ff4444', font=('Arial', 10, 'bold'))
        self.defense_status_label.pack(side='right', padx=10)
        
        # Sidebar
        sidebar = tk.Frame(self.root, bg='#0f3460', width=220)
        sidebar.pack(side='left', fill='y', padx=10, pady=10)
        sidebar.pack_propagate(False)
        
        buttons = [
            ("📊 DASHBOARD", "dashboard"),
            ("⚠️ AMEAÇAS", "threats"),
            ("🔥 FIREWALL", "firewall"),
            ("⚔️ CONTRA-ATAQUE", "counter"),
            ("🧠 IA", "ai"),
            ("📝 LOGS", "logs"),
            ("⚙️ CONFIG", "settings")
        ]
        
        self.tab_buttons = {}
        for text, name in buttons:
            btn = tk.Button(sidebar, text=text, command=lambda n=name: self.show_tab(n),
                           bg='#16213e', fg='white', font=('Arial', 11, 'bold'), 
                           padx=10, pady=12, cursor='hand2', relief='flat')
            btn.pack(pady=5, padx=10, fill='x')
            self.tab_buttons[name] = btn
        
        # Content
        self.content = tk.Frame(self.root, bg='#0a0a1a')
        self.content.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="✅ Sistema com IA Real | Ative a defesa para começar",
                                   bg='#0f3460', fg='#ccc', anchor='w', font=('Arial', 9))
        self.status_bar.pack(fill='x', side='bottom')
        
        # Tabs
        self.tabs = {
            "dashboard": DashboardTab(self.content, self),
            "threats": ThreatsTab(self.content, self),
            "firewall": FirewallTab(self.content, self),
            "counter": CounterTab(self.content, self),
            "ai": AITab(self.content, self),
            "logs": LogsTab(self.content, self),
            "settings": SettingsTab(self.content, self)
        }
        
        self.show_tab("dashboard")
        
    def setup_tray_icon(self):
        """Configura o ícone da bandeja do sistema"""
        if not SYSTEM_TRAY_AVAILABLE:
            return
        
        def create_tray_image():
            """Cria um ícone simples para a bandeja"""
            width = 64
            height = 64
            image = Image.new('RGB', (width, height), '#0f3460')
            draw = ImageDraw.Draw(image)
            
            # Desenhar um escudo
            draw.rectangle([10, 10, 54, 54], outline='#00ff88', width=3)
            draw.ellipse([20, 20, 44, 44], outline='#00ff88', width=2)
            draw.text((28, 28), "🛡️", fill='#00ff88')
            
            return image
        
        def on_quit():
            """Sair do aplicativo"""
            if self.is_defense_active:
                self.defense_engine.stop()
            self.tray_icon.stop()
            self.root.quit()
            os._exit(0)
        
        def show_window():
            """Mostrar a janela"""
            self.root.deiconify()
            self.root.lift()
            self.is_minimized = False
        
        # Criar menu da bandeja
        menu = pystray.Menu(
            pystray.MenuItem("🛡️ AI Security Suite", show_window, default=True),
            pystray.MenuItem("📊 Mostrar", show_window),
            pystray.MenuItem("🚪 Sair", on_quit)
        )
        
        self.tray_icon = pystray.Icon("ai_security", create_tray_image(), "AI Security Suite", menu)
    
    def minimize_to_tray(self):
        """Minimiza o aplicativo para a bandeja do sistema"""
        if SYSTEM_TRAY_AVAILABLE:
            self.root.withdraw()  # Esconder a janela
            self.is_minimized = True
            
            # Iniciar o ícone da bandeja em uma thread separada
            def run_tray():
                self.tray_icon.run()
            
            if not hasattr(self, '_tray_thread') or not self._tray_thread.is_alive():
                self._tray_thread = threading.Thread(target=run_tray, daemon=True)
                self._tray_thread.start()
            
            self.add_log("📌 Aplicativo minimizado para a bandeja do sistema", "info")
        else:
            # Fallback: minimizar normal
            self.minimize_window()
            self.add_log("⚠️ Systray não disponível. Minimizado normalmente.", "warning")
    
    def minimize_window(self):
        """Minimiza a janela normalmente"""
        self.root.iconify()
        self.add_log("📌 Aplicativo minimizado", "info")
    
    def on_closing(self):
        """Evento de fechamento da janela"""
        def quit_app():
            if self.is_defense_active:
                self.defense_engine.stop()
            if self.tray_icon:
                self.tray_icon.stop()
            self.root.quit()
            os._exit(0)
        
        # Se está na bandeja, só fechar se confirmar
        if self.is_minimized:
            quit_app()
        else:
            # Mostrar opções ao fechar
            result = tk.messagebox.askyesno(
                "Sair",
                "Deseja minimizar para a bandeja ou sair?\n\nSim = Minimizar para bandeja\nNão = Sair do programa"
            )
            if result:
                self.minimize_to_tray()
            else:
                quit_app()
    
    def add_log(self, msg, level="info"):
        """Adiciona mensagem ao log"""
        if hasattr(self, 'logs_tab'):
            self.logs_tab.add_log(msg, level)
        print(msg)
        
    def animate_defense_switch(self, active):
        if active:
            self.defense_switch_canvas.coords(self.defense_switch_btn, 33, 5, 53, 25)
            self.defense_switch_canvas.itemconfig(self.defense_switch_bg, fill='#00ff88')
            self.defense_switch_canvas.itemconfig(self.defense_switch_text, text="ON", fill='#0a0a1a')
            self.defense_status_label.config(text="DEFESA: ATIVA", fg='#00ff88')
            # Atualizar ícone da bandeja se disponível
            if self.tray_icon:
                self.tray_icon.title = "🛡️ DEFESA ATIVA"
        else:
            self.defense_switch_canvas.coords(self.defense_switch_btn, 5, 5, 25, 25)
            self.defense_switch_canvas.itemconfig(self.defense_switch_bg, fill='#555')
            self.defense_switch_canvas.itemconfig(self.defense_switch_text, text="OFF", fill='white')
            self.defense_status_label.config(text="DEFESA: INATIVA", fg='#ff4444')
            if self.tray_icon:
                self.tray_icon.title = "🛡️ DEFESA INATIVA"
            
    def toggle_defense(self, event=None):
        if not self.is_defense_active:
            self.defense_engine.start()
            self.is_defense_active = True
            self.animate_defense_switch(True)
            self.logs_tab.add_log("🚀 Defesa ATIVADA com IA Real", "success")
        else:
            self.defense_engine.stop()
            self.is_defense_active = False
            self.animate_defense_switch(False)
            self.logs_tab.add_log("🛑 Defesa DESATIVADA", "warning")
            
    def show_tab(self, name):
        for tab in self.tabs.values():
            tab.pack_forget()
        self.tabs[name].pack(fill='both', expand=True)
        for btn_name, btn in self.tab_buttons.items():
            if btn_name == name:
                btn.config(bg='#00ff88', fg='#0a0a1a')
            else:
                btn.config(bg='#16213e', fg='white')
                
    def handle_event(self, event):
        self.root.after(0, lambda: self.process_event(event))
        
    def process_event(self, event):
        if event.get("type") == "log":
            self.logs_tab.add_log(event.get("message", ""), event.get("level", "info"))
        elif event.get("type") == "counter_attack":
            self.counter_tab.add_attack_event(event)
        elif "source_ip" in event:
            self.threats_tab.add_threat(event)
            
    def start_updates(self):
        def update():
            while True:
                if self.is_defense_active and self.defense_engine:
                    stats = self.defense_engine.get_stats()
                    self.root.after(0, lambda: self.dashboard_tab.update_stats(stats))
                time.sleep(2)
        threading.Thread(target=update, daemon=True).start()
        
    @property
    def dashboard_tab(self): return self.tabs["dashboard"]
    @property
    def logs_tab(self): return self.tabs["logs"]
    @property
    def counter_tab(self): return self.tabs["counter"]
    @property
    def threats_tab(self): return self.tabs["threats"]
        
    def run(self):
        self.root.mainloop()
