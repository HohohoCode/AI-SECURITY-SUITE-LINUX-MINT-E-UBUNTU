import tkinter as tk
import threading
import time
import psutil
import subprocess

class DashboardTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='#0a0a1a')
        self.app = app
        self.setup_ui()
        self.start_monitoring()
        
    def setup_ui(self):
        # Título
        title_frame = tk.Frame(self, bg='#0a0a1a')
        title_frame.pack(fill='x', pady=15, padx=30)
        tk.Label(title_frame, text="📊 DASHBOARD", font=('Arial', 26, 'bold'),
                bg='#0a0a1a', fg='#00ff88').pack()
        tk.Label(title_frame, text="Monitoramento em tempo real", 
                bg='#0a0a1a', fg='#888', font=('Arial', 10)).pack()
        
        # Container principal para os cards (3x3)
        cards_container = tk.Frame(self, bg='#0a0a1a')
        cards_container.pack(fill='both', expand=True, padx=30, pady=10)
        
        # Configurar grid 3x3
        for i in range(3):
            cards_container.grid_columnconfigure(i, weight=1)
            cards_container.grid_rowconfigure(i, weight=1)
        
        # Definir todos os cards (9 cards)
        self.cards = {}
        
        cards_data = [
            # Linha 1
            ("🛡️", "AMEAÇAS DETECTADAS", "threats", "#ff4444", "0"),
            ("🚫", "IPs BLOQUEADOS", "blocked", "#ff8800", "0"),
            ("🔥", "FIREWALL", "firewall", "#ff6600", "VERIFICANDO"),
            # Linha 2
            ("📦", "PACOTES ANALISADOS", "packets", "#00ccff", "0"),
            ("🔗", "CONEXÕES ATIVAS", "connections", "#aa66ff", "0"),
            ("⏱️", "TEMPO ATIVO", "uptime", "#00ff88", "00:00:00"),
            # Linha 3
            ("💻", "CPU", "cpu", "#00ff88", "0%"),
            ("💾", "MEMÓRIA RAM", "memory", "#00ff88", "0%"),
            ("🎯", "NÍVEL DE RISCO", "risk", "#ffaa00", "BAIXO")
        ]
        
        for idx, (icon, title, key, color, default) in enumerate(cards_data):
            row = idx // 3
            col = idx % 3
            
            # Criar card
            card = tk.Frame(cards_container, bg='#16213e', relief='ridge', bd=2)
            card.grid(row=row, column=col, padx=8, pady=8, sticky='nsew')
            
            # Ícone e título
            title_frame_card = tk.Frame(card, bg='#16213e')
            title_frame_card.pack(fill='x', pady=(12, 5))
            tk.Label(title_frame_card, text=icon, bg='#16213e', fg=color, font=('Arial', 20)).pack(side='left', padx=(15, 5))
            tk.Label(title_frame_card, text=title, bg='#16213e', fg='#ccc', font=('Arial', 10, 'bold')).pack(side='left')
            
            # Valor
            if key == "firewall":
                value_font = ('Arial', 14, 'bold')
            else:
                value_font = ('Arial', 24, 'bold')
            
            self.cards[key] = tk.Label(card, text=default, bg='#16213e', fg=color, 
                                        font=value_font)
            self.cards[key].pack(pady=(5, 12))
        
        # Barra de status adicional na parte inferior
        status_bar = tk.Frame(self, bg='#16213e', relief='ridge', bd=2)
        status_bar.pack(fill='x', padx=30, pady=10)
        
        tk.Label(status_bar, text="🟢 STATUS DO SISTEMA", font=('Arial', 10, 'bold'),
                bg='#16213e', fg='#00ff88').pack(side='left', padx=15, pady=8)
        
        self.defense_status = tk.Label(status_bar, text="DEFESA: ATIVA", 
                                       bg='#16213e', fg='#00ff88', font=('Arial', 9, 'bold'))
        self.defense_status.pack(side='left', padx=15)
        
        self.last_update = tk.Label(status_bar, text="Última atualização: --:--:--", 
                                    bg='#16213e', fg='#888', font=('Arial', 8))
        self.last_update.pack(side='right', padx=15)
        
        # Atualizar firewall imediatamente
        self.update_firewall_status()
        
    def update_stats(self, stats):
        # Atualizar valores dos cards
        self.cards["threats"].config(text=str(stats.get("threats_detected", 0)))
        self.cards["blocked"].config(text=str(stats.get("threats_blocked", 0)))
        self.cards["packets"].config(text=str(stats.get("packets_analyzed", 0)))
        self.cards["connections"].config(text=str(stats.get("active_connections", 0)))
        
        # Calcular nível de risco baseado nas ameaças
        threats = stats.get("threats_detected", 0)
        if threats == 0:
            risk = "BAIXO"
            risk_color = "#00ff88"
        elif threats < 10:
            risk = "MÉDIO"
            risk_color = "#ffaa00"
        else:
            risk = "ALTO"
            risk_color = "#ff4444"
        
        self.cards["risk"].config(text=risk, fg=risk_color)
        
        # Atualizar uptime
        uptime = stats.get("uptime", 0)
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        self.cards["uptime"].config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        
        # Atualizar status da defesa
        if self.app.is_defense_active:
            self.defense_status.config(text="DEFESA: ATIVA", fg='#00ff88')
        else:
            self.defense_status.config(text="DEFESA: INATIVA", fg='#ff4444')
        
        # Atualizar timestamp
        from datetime import datetime
        self.last_update.config(text=f"Última atualização: {datetime.now().strftime('%H:%M:%S')}")
        
    def update_firewall_status(self):
        """Atualiza o status do firewall"""
        try:
            result = subprocess.run("sudo ufw status", shell=True, capture_output=True, text=True, timeout=5)
            if "Status: active" in result.stdout or "Estado: ativo" in result.stdout:
                self.cards["firewall"].config(text="ATIVO", fg='#00ff88')
            else:
                self.cards["firewall"].config(text="INATIVO", fg='#ff4444')
        except Exception as e:
            self.cards["firewall"].config(text="ERRO", fg='#ff4444')
        
        # Agendar próxima atualização
        self.after(3000, self.update_firewall_status)
        
    def update_system_resources(self):
        """Atualiza CPU e Memória"""
        try:
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().percent
            
            # CPU
            cpu_color = '#00ff88' if cpu < 70 else '#ffaa00' if cpu < 90 else '#ff4444'
            self.cards["cpu"].config(text=f"{cpu:.1f}%", fg=cpu_color)
            
            # Memória
            mem_color = '#00ff88' if mem < 70 else '#ffaa00' if mem < 90 else '#ff4444'
            self.cards["memory"].config(text=f"{mem:.1f}%", fg=mem_color)
            
        except Exception as e:
            pass
        
        # Agendar próxima atualização
        self.after(2000, self.update_system_resources)
        
    def start_monitoring(self):
        """Inicia o monitoramento"""
        self.update_system_resources()
