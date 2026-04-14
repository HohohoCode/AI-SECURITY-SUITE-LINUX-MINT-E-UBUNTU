import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
import time

class ThreatsTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='#0a0a1a')
        self.app = app
        self.setup_ui()
        self.start_auto_refresh()
        
    def setup_ui(self):
        title_frame = tk.Frame(self, bg='#0a0a1a')
        title_frame.pack(fill='x', pady=20, padx=30)
        tk.Label(title_frame, text="⚠️ AMEAÇAS DETECTADAS", font=('Arial', 24, 'bold'),
                bg='#0a0a1a', fg='#ff4444').pack()
        tk.Label(title_frame, text="Lista de todas as ameaças detectadas em tempo real", 
                bg='#0a0a1a', fg='#888', font=('Arial', 10)).pack()
        
        frame = tk.Frame(self, bg='#0a0a1a')
        frame.pack(fill='both', expand=True, padx=30, pady=10)
        
        scroll_y = ttk.Scrollbar(frame)
        scroll_y.pack(side='right', fill='y')
        
        scroll_x = ttk.Scrollbar(frame, orient='horizontal')
        scroll_x.pack(side='bottom', fill='x')
        
        self.tree = ttk.Treeview(frame, columns=("time", "type", "ip", "level", "action"), 
                                  show="headings", 
                                  yscrollcommand=scroll_y.set,
                                  xscrollcommand=scroll_x.set,
                                  height=20)
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        
        self.tree.heading("time", text="Data/Hora")
        self.tree.heading("type", text="Tipo de Ameaça")
        self.tree.heading("ip", text="IP Origem")
        self.tree.heading("level", text="Nível")
        self.tree.heading("action", text="Ação Tomada")
        
        self.tree.column("time", width=160, minwidth=160)
        self.tree.column("type", width=150, minwidth=120)
        self.tree.column("ip", width=150, minwidth=120)
        self.tree.column("level", width=80, minwidth=80)
        self.tree.column("action", width=120, minwidth=100)
        
        self.tree.pack(fill='both', expand=True)
        
        self.tree.tag_configure("CRITICAL", foreground="#ff4444", font=('Arial', 10, 'bold'))
        self.tree.tag_configure("HIGH", foreground="#ff8800", font=('Arial', 10, 'bold'))
        self.tree.tag_configure("MEDIUM", foreground="#ffaa00")
        self.tree.tag_configure("LOW", foreground="#00ff88")
        
        btn_frame = tk.Frame(self, bg='#0a0a1a')
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="🗑️ LIMPAR HISTÓRICO", command=self.clear_threats,
                 bg='#ff4444', fg='white', font=('Arial', 10, 'bold'), padx=20, pady=5, cursor='hand2').pack()
        
        self.count_label = tk.Label(self, text="Total de ameaças: 0", bg='#0a0a1a', fg='#888', font=('Arial', 10))
        self.count_label.pack(pady=5)
        
    def refresh_list(self):
        """Atualiza a lista de ameaças (chamado pela thread principal via after)"""
        if not self.app.defense_engine:
            return
        
        threats = self.app.defense_engine.get_threats()
        
        # Limpar a treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Adicionar todas as ameaças
        for threat in threats:
            self.add_threat(threat)
        
        # Atualizar contagem
        self.count_label.config(text=f"Total de ameaças: {len(threats)}")
        
    def add_threat(self, threat):
        time_str = datetime.fromtimestamp(threat.get("timestamp", time.time())).strftime("%Y-%m-%d %H:%M:%S")
        level = threat.get("level", "MEDIUM").upper()
        threat_type = threat.get("type", "Unknown")
        source_ip = threat.get("source_ip", "N/A")
        action = threat.get("action", "Bloqueado")
        
        self.tree.insert("", 0, values=(time_str, threat_type, source_ip, level, action), tags=(level,))
        
    def clear_threats(self):
        if messagebox.askyesno("Confirmar", "Limpar todo o histórico de ameaças?"):
            for item in self.tree.get_children():
                self.tree.delete(item)
            if self.app.defense_engine:
                self.app.defense_engine.threats = []
            self.count_label.config(text="Total de ameaças: 0")
            self.app.logs_tab.add_log("Histórico de ameaças limpo", "info")
        
    def start_auto_refresh(self):
        """Atualização automática usando after (thread principal)"""
        def refresh():
            self.refresh_list()
            self.after(2000, refresh)  # Atualiza a cada 2 segundos
        self.after(1000, refresh)
