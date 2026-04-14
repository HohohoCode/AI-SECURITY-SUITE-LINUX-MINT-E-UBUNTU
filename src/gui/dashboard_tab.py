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
        title_frame.pack(fill='x', pady=20, padx=30)
        tk.Label(title_frame, text="📊 DASHBOARD", font=('Arial', 28, 'bold'),
                bg='#0a0a1a', fg='#00ff88').pack()
        tk.Label(title_frame, text="Monitoramento em tempo real", 
                bg='#0a0a1a', fg='#888', font=('Arial', 11)).pack()
        
        # Cards - Linha 1
        cards_frame1 = tk.Frame(self, bg='#0a0a1a')
        cards_frame1.pack(fill='x', padx=30, pady=10)
        
        # Card Ameaças
        c1 = tk.Frame(cards_frame1, bg='#16213e', relief='ridge', bd=2, width=220, height=130)
        c1.pack(side='left', padx=10, expand=True, fill='both')
        c1.pack_propagate(False)
        tk.Label(c1, text="🛡️ AMEAÇAS", bg='#16213e', fg='#ff4444', font=('Arial', 12, 'bold')).pack(pady=(15,5))
        self.threats_label = tk.Label(c1, text="0", bg='#16213e', fg='#ff4444', font=('Arial', 32, 'bold'))
        self.threats_label.pack()
        
        # Card Bloqueios
        c2 = tk.Frame(cards_frame1, bg='#16213e', relief='ridge', bd=2, width=220, height=130)
        c2.pack(side='left', padx=10, expand=True, fill='both')
        c2.pack_propagate(False)
        tk.Label(c2, text="🚫 BLOQUEIOS", bg='#16213e', fg='#ff8800', font=('Arial', 12, 'bold')).pack(pady=(15,5))
        self.blocked_label = tk.Label(c2, text="0", bg='#16213e', fg='#ff8800', font=('Arial', 32, 'bold'))
        self.blocked_label.pack()
        
        # Card Firewall
        c3 = tk.Frame(cards_frame1, bg='#16213e', relief='ridge', bd=2, width=220, height=130)
        c3.pack(side='left', padx=10, expand=True, fill='both')
        c3.pack_propagate(False)
        tk.Label(c3, text="🔥 FIREWALL", bg='#16213e', fg='#ff6600', font=('Arial', 12, 'bold')).pack(pady=(15,5))
        self.firewall_label = tk.Label(c3, text="VERIFICANDO...", bg='#16213e', fg='#ff6600', font=('Arial', 16, 'bold'))
        self.firewall_label.pack()
        
        # Cards - Linha 2
        cards_frame2 = tk.Frame(self, bg='#0a0a1a')
        cards_frame2.pack(fill='x', padx=30, pady=10)
        
        # Card Pacotes
        c4 = tk.Frame(cards_frame2, bg='#16213e', relief='ridge', bd=2, width=220, height=130)
        c4.pack(side='left', padx=10, expand=True, fill='both')
        c4.pack_propagate(False)
        tk.Label(c4, text="📦 PACOTES", bg='#16213e', fg='#00ccff', font=('Arial', 12, 'bold')).pack(pady=(15,5))
        self.packets_label = tk.Label(c4, text="0", bg='#16213e', fg='#00ccff', font=('Arial', 32, 'bold'))
        self.packets_label.pack()
        
        # Card Conexões
        c5 = tk.Frame(cards_frame2, bg='#16213e', relief='ridge', bd=2, width=220, height=130)
        c5.pack(side='left', padx=10, expand=True, fill='both')
        c5.pack_propagate(False)
        tk.Label(c5, text="🔗 CONEXÕES", bg='#16213e', fg='#aa66ff', font=('Arial', 12, 'bold')).pack(pady=(15,5))
        self.conn_label = tk.Label(c5, text="0", bg='#16213e', fg='#aa66ff', font=('Arial', 32, 'bold'))
        self.conn_label.pack()
        
        # Card Tempo Ativo
        c6 = tk.Frame(cards_frame2, bg='#16213e', relief='ridge', bd=2, width=220, height=130)
        c6.pack(side='left', padx=10, expand=True, fill='both')
        c6.pack_propagate(False)
        tk.Label(c6, text="⏱️ TEMPO ATIVO", bg='#16213e', fg='#00ff88', font=('Arial', 12, 'bold')).pack(pady=(15,5))
        self.uptime_label = tk.Label(c6, text="00:00:00", bg='#16213e', fg='#00ff88', font=('Arial', 20, 'bold'))
        self.uptime_label.pack()
        
        # Status do Sistema
        sys_frame = tk.Frame(self, bg='#16213e', relief='ridge', bd=2)
        sys_frame.pack(fill='x', padx=30, pady=10)
        
        tk.Label(sys_frame, text="🖥️ STATUS DO SISTEMA", font=('Arial', 14, 'bold'),
                bg='#16213e', fg='#00ff88').pack(pady=10)
        
        status_grid = tk.Frame(sys_frame, bg='#16213e')
        status_grid.pack(fill='x', padx=20, pady=10)
        
        # Firewall
        f1 = tk.Frame(status_grid, bg='#0f3460', relief='ridge', bd=1, width=200, height=60)
        f1.pack(side='left', padx=5, pady=5, expand=True, fill='both')
        f1.pack_propagate(False)
        tk.Label(f1, text="🔥 FIREWALL", bg='#0f3460', fg='#ff6600', font=('Arial', 10, 'bold')).pack(pady=(5,0))
        self.fw_status = tk.Label(f1, text="Verificando...", bg='#0f3460', fg='white', font=('Arial', 11))
        self.fw_status.pack()
        
        # Defesa
        f2 = tk.Frame(status_grid, bg='#0f3460', relief='ridge', bd=1, width=200, height=60)
        f2.pack(side='left', padx=5, pady=5, expand=True, fill='both')
        f2.pack_propagate(False)
        tk.Label(f2, text="🛡️ DEFESA", bg='#0f3460', fg='#00ff88', font=('Arial', 10, 'bold')).pack(pady=(5,0))
        self.defense_status = tk.Label(f2, text="Inativa", bg='#0f3460', fg='white', font=('Arial', 11))
        self.defense_status.pack()
        
        # CPU
        f3 = tk.Frame(status_grid, bg='#0f3460', relief='ridge', bd=1, width=200, height=60)
        f3.pack(side='left', padx=5, pady=5, expand=True, fill='both')
        f3.pack_propagate(False)
        tk.Label(f3, text="💻 CPU", bg='#0f3460', fg='#00ccff', font=('Arial', 10, 'bold')).pack(pady=(5,0))
        self.cpu_label = tk.Label(f3, text="0%", bg='#0f3460', fg='white', font=('Arial', 11))
        self.cpu_label.pack()
        
        # Memória
        f4 = tk.Frame(status_grid, bg='#0f3460', relief='ridge', bd=1, width=200, height=60)
        f4.pack(side='left', padx=5, pady=5, expand=True, fill='both')
        f4.pack_propagate(False)
        tk.Label(f4, text="💾 MEMÓRIA", bg='#0f3460', fg='#aa66ff', font=('Arial', 10, 'bold')).pack(pady=(5,0))
        self.mem_label = tk.Label(f4, text="0%", bg='#0f3460', fg='white', font=('Arial', 11))
        self.mem_label.pack()
        
        # Atualizar firewall imediatamente
        self.update_firewall_status()
        
    def update_stats(self, stats):
        self.threats_label.config(text=str(stats.get("threats_detected", 0)))
        self.blocked_label.config(text=str(stats.get("threats_blocked", 0)))
        self.packets_label.config(text=str(stats.get("packets_analyzed", 0)))
        self.conn_label.config(text=str(stats.get("active_connections", 0)))
        
        uptime = stats.get("uptime", 0)
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        self.uptime_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        
        if self.app.is_defense_active:
            self.defense_status.config(text="ATIVA", fg='#00ff88')
        else:
            self.defense_status.config(text="Inativa", fg='#ff4444')
            
    def update_firewall_status(self):
        """Atualiza o status do firewall verificando diretamente o UFW"""
        try:
            result = subprocess.run("sudo ufw status", shell=True, capture_output=True, text=True, timeout=5)
            if "Status: active" in result.stdout or "Estado: ativo" in result.stdout:
                # Firewall está ATIVO
                self.firewall_label.config(text="ATIVO", fg='#00ff88')
                self.fw_status.config(text="ATIVO", fg='#00ff88')
            else:
                # Firewall está INATIVO
                self.firewall_label.config(text="INATIVO", fg='#ff4444')
                self.fw_status.config(text="INATIVO", fg='#ff4444')
        except Exception as e:
            self.firewall_label.config(text="ERRO", fg='#ff4444')
            self.fw_status.config(text="ERRO", fg='#ff4444')
        
        # Agendar próxima atualização
        self.after(2000, self.update_firewall_status)
        
    def start_monitoring(self):
        def monitor():
            while True:
                if self.winfo_exists():
                    try:
                        cpu = psutil.cpu_percent()
                        mem = psutil.virtual_memory().percent
                        self.cpu_label.config(text=f"{cpu:.1f}%", fg='#00ff88' if cpu < 80 else '#ff4444')
                        self.mem_label.config(text=f"{mem:.1f}%", fg='#00ff88' if mem < 80 else '#ff4444')
                    except:
                        pass
                time.sleep(2)
        threading.Thread(target=monitor, daemon=True).start()
