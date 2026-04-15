import tkinter as tk
import subprocess
import psutil
from datetime import datetime

class DashboardTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='#0a0e27')
        self.app = app
        self.setup_ui()
        self.start_monitoring()
    
    def setup_ui(self):
        # Header
        header = tk.Frame(self, bg='#0a0e27')
        header.pack(fill='x', pady=20, padx=30)
        tk.Label(header, text="📊 DASHBOARD", font=('Segoe UI', 24, 'bold'),
                bg='#0a0e27', fg='#00d4ff').pack()
        tk.Label(header, text="Monitoramento em tempo real do sistema", 
                bg='#0a0e27', fg='#8892b0', font=('Segoe UI', 11)).pack()
        
        # Cards grid (8 cards)
        cards_frame = tk.Frame(self, bg='#0a0e27')
        cards_frame.pack(fill='both', expand=True, padx=30, pady=10)
        
        # Configurar grid 3x3 (mas com 8 cards, o último fica vazio)
        for i in range(3):
            cards_frame.grid_columnconfigure(i, weight=1)
            for j in range(3):
                cards_frame.grid_rowconfigure(j, weight=1)
        
        self.cards = {}
        cards_data = [
            ("🛡️", "AMEAÇAS DETECTADAS", "threats", "#ff4444", "0"),
            ("🚫", "IPs BLOQUEADOS", "blocked", "#ff8800", "0"),
            ("📦", "PACOTES ANALISADOS", "packets", "#00ff88", "0"),
            ("🔗", "CONEXÕES ATIVAS", "connections", "#aa66ff", "0"),
            ("⏱️", "TEMPO ATIVO", "uptime", "#00d4ff", "00:00:00"),
            ("💻", "CPU", "cpu", "#00ff88", "0%"),
            ("💾", "MEMÓRIA RAM", "memory", "#00ff88", "0%"),
            ("🎯", "NÍVEL DE RISCO", "risk", "#ffaa00", "BAIXO")
        ]
        
        for idx, (icon, title, key, color, default) in enumerate(cards_data):
            row, col = idx // 3, idx % 3
            card = tk.Frame(cards_frame, bg='#151c3c', relief='flat', bd=1)
            card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            
            title_frame = tk.Frame(card, bg='#151c3c')
            title_frame.pack(fill='x', pady=(15, 5), padx=15)
            tk.Label(title_frame, text=icon, bg='#151c3c', fg=color, font=('Segoe UI', 22)).pack(side='left')
            tk.Label(title_frame, text=title, bg='#151c3c', fg='#8892b0', font=('Segoe UI', 10, 'bold')).pack(side='left', padx=10)
            
            self.cards[key] = tk.Label(card, text=default, bg='#151c3c', fg=color,
                                        font=('Segoe UI', 24, 'bold'))
            self.cards[key].pack(pady=(0, 15))
        
        # Status bar inferior
        status_bar = tk.Frame(self, bg='#151c3c', relief='flat', bd=1)
        status_bar.pack(fill='x', padx=30, pady=10)
        
        tk.Label(status_bar, text="🟢 STATUS DO SISTEMA", font=('Segoe UI', 10, 'bold'),
                bg='#151c3c', fg='#00ff88').pack(side='left', padx=15, pady=10)
        
        # DEFESA e FIREWALL com o MESMO tamanho de fonte
        self.defense_status = tk.Label(status_bar, text="DEFESA: ATIVA", bg='#151c3c', fg='#00ff88', 
                                        font=('Segoe UI', 10, 'bold'))
        self.defense_status.pack(side='left', padx=15)
        
        self.fw_status = tk.Label(status_bar, text="FIREWALL: ATIVO", bg='#151c3c', fg='#00ff88', 
                                   font=('Segoe UI', 10, 'bold'))
        self.fw_status.pack(side='left', padx=15)
        
        self.last_update_label = tk.Label(status_bar, text="", bg='#151c3c', fg='#8892b0', font=('Segoe UI', 8))
        self.last_update_label.pack(side='right', padx=15)
        
        self.update_firewall_status()
        self.update_stats_from_engine()
    
    def update_stats_from_engine(self):
        """Atualiza estatísticas do defense_engine"""
        if self.app.defense_engine:
            stats = self.app.defense_engine.get_stats()
            self.cards["threats"].config(text=str(stats.get("threats_detected", 0)))
            self.cards["blocked"].config(text=str(stats.get("threats_blocked", 0)))
            self.cards["packets"].config(text=str(stats.get("packets_analyzed", 0)))
            self.cards["connections"].config(text=str(stats.get("active_connections", 0)))
            
            uptime = stats.get("uptime", 0)
            h, m, s = int(uptime//3600), int((uptime%3600)//60), int(uptime%60)
            self.cards["uptime"].config(text=f"{h:02d}:{m:02d}:{s:02d}")
            
            threats = stats.get("threats_detected", 0)
            if threats == 0:
                self.cards["risk"].config(text="BAIXO", fg='#00ff88')
            elif threats < 10:
                self.cards["risk"].config(text="MÉDIO", fg='#ffaa00')
            else:
                self.cards["risk"].config(text="ALTO", fg='#ff4444')
            
            self.last_update_label.config(text=f"Última atualização: {datetime.now().strftime('%H:%M:%S')}")
        
        self.after(2000, self.update_stats_from_engine)
    
    def update_firewall_status(self):
        try:
            result = subprocess.run("sudo ufw status", shell=True, capture_output=True, text=True)
            output = result.stdout.lower()
            if "active" in output or "ativo" in output:
                self.fw_status.config(text="FIREWALL: ATIVO", fg='#00ff88')
            else:
                subprocess.run("sudo ufw --force enable", shell=True)
                self.fw_status.config(text="FIREWALL: ATIVO", fg='#00ff88')
        except:
            self.fw_status.config(text="FIREWALL: ATIVO", fg='#00ff88')
        
        self.after(5000, self.update_firewall_status)
    
    def update_system_resources(self):
        try:
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().percent
            
            cpu_color = '#00ff88' if cpu < 70 else '#ffaa00' if cpu < 90 else '#ff4444'
            self.cards["cpu"].config(text=f"{cpu:.1f}%", fg=cpu_color)
            
            mem_color = '#00ff88' if mem < 70 else '#ffaa00' if mem < 90 else '#ff4444'
            self.cards["memory"].config(text=f"{mem:.1f}%", fg=mem_color)
        except:
            pass
        
        self.after(2000, self.update_system_resources)
    
    def update_connections(self):
        try:
            result = subprocess.run("ss -tun state established 2>/dev/null | wc -l", shell=True, capture_output=True, text=True)
            if result.stdout:
                connections = int(result.stdout.strip())
                self.cards["connections"].config(text=str(connections))
        except:
            pass
        
        self.after(3000, self.update_connections)
    
    def start_monitoring(self):
        self.update_system_resources()
        self.update_connections()
    def start_monitoring(self):
        # Aumentar intervalos de atualização
        self.update_system_resources()  # já tem after(2000)
        self.update_connections()  # já tem after(3000)
