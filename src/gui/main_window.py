import tkinter as tk
import threading
import time
import subprocess
from datetime import datetime

from src.config.settings import Settings
from src.core.defense_engine import DefenseEngine
from src.core.counter_attack import CounterAttack
from src.gui.dashboard_tab import DashboardTab
from src.gui.threats_tab import ThreatsTab
from src.gui.firewall_tab import FirewallTab
from src.gui.counter_tab import CounterTab
from src.gui.logs_tab import LogsTab
from src.gui.ai_tab import AITab
from src.gui.connections_tab import ConnectionsTab

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🛡️ AI SECURITY SUITE PRO")
        self.root.geometry("1400x900")
        self.root.configure(bg='#0a0e27')
        self.root.minsize(1200, 750)
        
        self.settings = Settings()
        self.defense_engine = DefenseEngine(self.settings, self.handle_event)
        self.counter_attack = CounterAttack(self.settings, self.handle_event)
        
        self.setup_ui()
        self.start_updates()
        self.check_firewall_status()
    
    def check_firewall_status(self):
        try:
            result = subprocess.run("sudo ufw status", shell=True, capture_output=True, text=True)
            if "inactive" in result.stdout.lower():
                subprocess.run("sudo ufw --force enable", shell=True)
                subprocess.run("sudo ufw default deny incoming", shell=True)
                subprocess.run("sudo ufw default allow outgoing", shell=True)
                print("🔥 Firewall ativado")
        except:
            pass
    
    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg='#0f1535', height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        title_frame = tk.Frame(header, bg='#0f1535')
        title_frame.pack(side='left', padx=30, pady=10)
        
        tk.Label(title_frame, text="🛡️", font=('Segoe UI', 28), bg='#0f1535', fg='#00d4ff').pack(side='left')
        tk.Label(title_frame, text="AI SECURITY SUITE", font=('Segoe UI', 16, 'bold'),
                bg='#0f1535', fg='#ffffff').pack(side='left', padx=10)
        tk.Label(title_frame, text="PRO", font=('Segoe UI', 10, 'bold'),
                bg='#00d4ff', fg='#0a0e27', padx=6, pady=2).pack(side='left')
        
        # Sidebar (sem estatísticas)
        sidebar = tk.Frame(self.root, bg='#0f1535', width=240)
        sidebar.pack(side='left', fill='y', padx=10, pady=10)
        sidebar.pack_propagate(False)
        
        menu_items = [
            ("📊 DASHBOARD", "dashboard", "#00d4ff"),
            ("⚠️ AMEAÇAS", "threats", "#ff4444"),
            ("🚫 IPs BLOQUEADOS", "firewall", "#ff8800"),
            ("⚔️ CONTRA-ATAQUE", "counter", "#00ff88"),
            ("🔗 CONEXÕES", "connections", "#aa66ff"),
            ("🧠 IA", "ai", "#00d4ff"),
            ("📝 LOGS", "logs", "#ffffff")
        ]
        
        self.tab_buttons = {}
        for text, name, color in menu_items:
            btn = tk.Button(sidebar, text=text, command=lambda n=name: self.show_tab(n),
                           bg='#1a2352', fg=color, font=('Segoe UI', 11, 'bold'),
                           padx=15, pady=12, cursor='hand2', relief='flat',
                           anchor='w', width=20)
            btn.pack(pady=8, padx=15, fill='x')
            self.tab_buttons[name] = btn
        
        # Separador
        tk.Frame(sidebar, bg='#1a2352', height=2).pack(fill='x', pady=15, padx=15)
        
        self.content = tk.Frame(self.root, bg='#0a0e27')
        self.content.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        status_frame = tk.Frame(self.root, bg='#0f1535', height=35)
        status_frame.pack(fill='x', side='bottom')
        status_frame.pack_propagate(False)
        
        self.status_text = tk.Label(status_frame, text="✅ SISTEMA OPERACIONAL | IA ATIVA | MONITORANDO",
                                   bg='#0f1535', fg='#00ff88', anchor='w', font=('Segoe UI', 9))
        self.status_text.pack(side='left', padx=20, fill='x', expand=True)
        
        self.clock_label = tk.Label(status_frame, text="", bg='#0f1535', fg='#8892b0', font=('Segoe UI', 9))
        self.clock_label.pack(side='right', padx=20)
        self.update_clock()
        
        self.tabs = {
            "dashboard": DashboardTab(self.content, self),
            "threats": ThreatsTab(self.content, self),
            "firewall": FirewallTab(self.content, self),
            "counter": CounterTab(self.content, self),
            "connections": ConnectionsTab(self.content, self),
            "ai": AITab(self.content, self),
            "logs": LogsTab(self.content, self)
        }
        
        self.show_tab("dashboard")
    
    def update_clock(self):
        from datetime import datetime
        self.clock_label.config(text=datetime.now().strftime("%H:%M:%S - %d/%m/%Y"))
        self.root.after(1000, self.update_clock)
    
    def show_tab(self, name):
        for tab in self.tabs.values():
            tab.pack_forget()
        self.tabs[name].pack(fill='both', expand=True)
        for btn_name, btn in self.tab_buttons.items():
            if btn_name == name:
                btn.config(bg='#00d4ff', fg='#0a0e27')
            else:
                btn.config(bg='#1a2352', fg='#ffffff')
    
    def handle_event(self, event):
        self.root.after(0, lambda: self.process_event(event))
    
    def process_event(self, event):
        if event.get("type") == "log":
            self.logs_tab.add_log(event.get("message", ""))
        elif event.get("type") == "counter_attack":
            self.counter_tab.add_attack_event(event)
        elif "source_ip" in event or "ip" in event:
            self.threats_tab.add_threat(event)
            self.dashboard_tab.update_stats_from_engine()
    
    def start_updates(self):
        def update_sidebar():
            if self.defense_engine:
                stats = self.defense_engine.get_stats()
                self.dashboard_tab.update_stats_from_engine()
            self.root.after(2000, update_sidebar)
        
        update_sidebar()
    
    @property
    def dashboard_tab(self): 
        return self.tabs["dashboard"]
    
    @property
    def logs_tab(self): 
        return self.tabs["logs"]
    
    @property
    def counter_tab(self): 
        return self.tabs["counter"]
    
    @property
    def threats_tab(self): 
        return self.tabs["threats"]
    
    def run(self):
        self.root.mainloop()
    def start_updates(self):
        def update_sidebar():
            if self.defense_engine:
                stats = self.defense_engine.get_stats()
                self.dashboard_tab.update_stats_from_engine()
            self.root.after(5000, update_sidebar)  # Aumentado para 5 segundos (antes 2)
        
        update_sidebar()
