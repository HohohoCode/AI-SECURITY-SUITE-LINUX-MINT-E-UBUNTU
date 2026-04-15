import tkinter as tk
import threading
import time
from datetime import datetime
import os

from src.config.settings import Settings
from src.core.defense_engine import DefenseEngine
from src.core.counter_attack import CounterAttack
from src.gui.dashboard_tab import DashboardTab
from src.gui.threats_tab import ThreatsTab
from src.gui.firewall_tab import FirewallTab
from src.gui.counter_tab import CounterTab
from src.gui.logs_tab import LogsTab
from src.gui.ai_tab import AITab
from src.gui.advanced_dashboard import AdvancedDashboard

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🛡️ AI Security Suite Pro - Defesa Total")
        self.root.geometry("1400x900")
        self.root.configure(bg='#0a0a1a')
        self.root.minsize(1200, 700)
        
        self.settings = Settings()
        self.settings.set("sensitivity", 100)
        self.settings.set("auto_block", True)
        self.settings.set("auto_counter", True)
        
        self.defense_engine = DefenseEngine(self.settings, self.handle_event)
        self.counter_attack = CounterAttack(self.settings, self.handle_event)
        
        self.defense_engine.start()
        self.is_defense_active = True
        
        self.setup_ui()
        self.start_updates()
        self.activate_firewall()
        
    def activate_firewall(self):
        import subprocess
        try:
            subprocess.run("sudo ufw --force enable", shell=True, capture_output=True)
            print("🔥 Firewall ativado automaticamente")
        except:
            pass
        
    def setup_ui(self):
        header = tk.Frame(self.root, bg='#0f3460', height=70)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text="🛡️ AI SECURITY SUITE PRO", font=('Arial', 20, 'bold'),
                bg='#0f3460', fg='#00ff88').pack(side='left', padx=30)
        
        tk.Label(header, text="✅ DEFESA TOTAL | 7 CAMADAS | IA AVANÇADA", 
                bg='#00ff88', fg='#0a0a1a', font=('Arial', 10, 'bold'), padx=15, pady=5).pack(side='left', padx=20)
        
        tk.Label(header, text="🛡️", font=('Arial', 24),
                bg='#0f3460', fg='#00ff88').pack(side='right', padx=30)
        
        sidebar = tk.Frame(self.root, bg='#0f3460', width=240)
        sidebar.pack(side='left', fill='y', padx=10, pady=10)
        sidebar.pack_propagate(False)
        
        buttons = [
            ("📊 DASHBOARD", "dashboard"),
            ("⚠️ AMEAÇAS", "threats"),
            ("🚫 IPs BLOQUEADOS", "firewall"),
            ("⚔️ CONTRA-ATAQUE", "counter"),
            ("📈 DASHBOARD AVANÇADO", "adv_dashboard"),
            ("🧠 IA", "ai"),
            ("📝 LOGS", "logs")
        ]
        
        self.tab_buttons = {}
        for text, name in buttons:
            btn = tk.Button(sidebar, text=text, command=lambda n=name: self.show_tab(n),
                           bg='#16213e', fg='white', font=('Arial', 11, 'bold'), 
                           padx=10, pady=12, cursor='hand2', relief='flat')
            btn.pack(pady=5, padx=10, fill='x')
            self.tab_buttons[name] = btn
        
        self.content = tk.Frame(self.root, bg='#0a0a1a')
        self.content.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        self.status_bar = tk.Label(self.root, text="✅ SISTEMA DE DEFESA TOTAL ATIVO | 7 Camadas de Proteção",
                                   bg='#0f3460', fg='#00ff88', anchor='w', font=('Arial', 9))
        self.status_bar.pack(fill='x', side='bottom')
        
        self.tabs = {
            "dashboard": DashboardTab(self.content, self),
            "threats": ThreatsTab(self.content, self),
            "firewall": FirewallTab(self.content, self),
            "counter": CounterTab(self.content, self),
            "adv_dashboard": AdvancedDashboard(self.content, self),
            "ai": AITab(self.content, self),
            "logs": LogsTab(self.content, self)
        }
        
        self.show_tab("dashboard")
        
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
                if self.defense_engine:
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
