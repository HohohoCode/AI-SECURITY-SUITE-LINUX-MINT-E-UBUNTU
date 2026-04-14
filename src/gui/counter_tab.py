import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime

class CounterTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='#0a0a1a')
        self.app = app
        self.setup_ui()
        
    def setup_ui(self):
        # Título
        title_frame = tk.Frame(self, bg='#0a0a1a')
        title_frame.pack(fill='x', pady=20, padx=30)
        tk.Label(title_frame, text="⚔️ CONTRA-ATAQUE AUTOMÁTICO", font=('Arial', 24, 'bold'),
                bg='#0a0a1a', fg='#00ccff').pack()
        tk.Label(title_frame, text="Sistema automático de resposta a invasores", 
                bg='#0a0a1a', fg='#888').pack()
        
        # Informações
        info_frame = tk.Frame(self, bg='#16213e', relief='ridge', bd=2)
        info_frame.pack(fill='x', padx=30, pady=10)
        tk.Label(info_frame, text="🤖 O sistema opera AUTOMATICAMENTE quando ameaças são detectadas\n\n"
                 "✓ Detecta o IP do invasor\n"
                 "✓ Coleta WHOIS e geolocalização\n"
                 "✓ Bloqueia o IP automaticamente\n"
                 "✓ Registra todas as ações",
                 bg='#16213e', fg='#00ff88', justify='left', font=('Arial', 11)).pack(pady=20, padx=20)
        
        # Histórico
        history_frame = tk.LabelFrame(self, text="📜 HISTÓRICO DE CONTRA-ATAQUES", bg='#16213e', fg='#ff8800', font=('Arial', 12, 'bold'))
        history_frame.pack(fill='both', expand=True, padx=30, pady=10)
        
        self.history_text = scrolledtext.ScrolledText(history_frame, bg='#0a0a1a', fg='#ff8800', font=('Courier', 10), height=20)
        self.history_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.add_history("📋 Sistema de contra-ataque automático inicializado")
        self.add_history("⚡ Aguardando detecção de ameaças...")
        
    def add_attack_event(self, event):
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        self.add_history(f"\n{'='*50}")
        self.add_history(f"[{ts}] 🎯 CONTRA-ATAQUE AUTOMÁTICO")
        self.add_history(f"📍 IP Atacante: {event.get('ip', 'N/A')}")
        self.add_history(f"⚠️ Tipo de Ameaça: {event.get('threat', 'N/A')}")
        for info in event.get('info', []):
            self.add_history(f"   {info}")
        self.add_history(f"✅ Ação: IP bloqueado automaticamente")
        self.add_history(f"{'='*50}\n")
        
    def add_history(self, msg):
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        self.history_text.insert('end', f"[{ts}] {msg}\n")
        self.history_text.see('end')
