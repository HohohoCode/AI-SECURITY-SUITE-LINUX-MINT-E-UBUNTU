import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import time

class ThreatsTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='#0a0a1a')
        self.app = app
        self.setup_ui()
    
    def setup_ui(self):
        tk.Label(self, text="⚠️ AMEAÇAS", font=('Arial', 24, 'bold'),
                bg='#0a0a1a', fg='#ff4444').pack(pady=20)
        
        frame = tk.Frame(self, bg='#0a0a1a')
        frame.pack(fill='both', expand=True, padx=30, pady=10)
        
        scroll_y = ttk.Scrollbar(frame)
        scroll_y.pack(side='right', fill='y')
        
        self.tree = ttk.Treeview(frame, columns=("time", "type", "ip", "level"),
                                  show="headings", yscrollcommand=scroll_y.set, height=18)
        scroll_y.config(command=self.tree.yview)
        
        self.tree.heading("time", text="Data/Hora")
        self.tree.heading("type", text="Tipo")
        self.tree.heading("ip", text="IP Origem")
        self.tree.heading("level", text="Nível")
        
        self.tree.column("time", width=150)
        self.tree.column("type", width=120)
        self.tree.column("ip", width=140)
        self.tree.column("level", width=80)
        
        self.tree.pack(fill='both', expand=True)
        self.tree.tag_configure("CRITICAL", foreground="#ff4444")
        self.tree.tag_configure("HIGH", foreground="#ff8800")
        
        tk.Button(self, text="🗑️ LIMPAR", command=self.clear,
                 bg='#ff4444', fg='white', padx=20, pady=5, cursor='hand2').pack(pady=10)
        
        self.refresh_list()
    
    def add_threat(self, threat):
        ts = datetime.fromtimestamp(threat.get("timestamp", time.time())).strftime("%Y-%m-%d %H:%M:%S")
        level = threat.get("level", "HIGH")
        ip = threat.get("source_ip") or threat.get("ip", "N/A")
        t_type = threat.get("type", "UNKNOWN")
        self.tree.insert("", 0, values=(ts, t_type, ip, level), tags=(level,))
    
    def clear(self):
        if messagebox.askyesno("Confirmar", "Limpar todas as ameaças?"):
            for item in self.tree.get_children():
                self.tree.delete(item)
    
    def refresh_list(self):
        if self.app.defense_engine:
            threats = self.app.defense_engine.get_threats()
            if len(self.tree.get_children()) != len(threats):
                for item in self.tree.get_children():
                    self.tree.delete(item)
                for threat in threats:
                    self.add_threat(threat)
        self.after(3000, self.refresh_list)
