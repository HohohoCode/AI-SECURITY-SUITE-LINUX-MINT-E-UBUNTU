import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime

class CounterTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='#0a0a1a')
        self.app = app
        self.setup_ui()
        
    def setup_ui(self):
        title_frame = tk.Frame(self, bg='#0a0a1a')
        title_frame.pack(fill='x', pady=20, padx=30)
        tk.Label(title_frame, text="⚔️ CONTRA-ATAQUE AUTOMÁTICO", font=('Arial', 24, 'bold'),
                bg='#0a0a1a', fg='#00ccff').pack()
        tk.Label(title_frame, text="Sistema automático de resposta a invasores", 
                bg='#0a0a1a', fg='#888', font=('Arial', 10)).pack()
        
        info_frame = tk.Frame(self, bg='#16213e', relief='ridge', bd=2)
        info_frame.pack(fill='x', padx=30, pady=10)
        tk.Label(info_frame, text="🤖 O sistema opera AUTOMATICAMENTE quando ameaças são detectadas\n\n"
                 "✓ Detecta o IP do invasor\n"
                 "✓ Coleta WHOIS e geolocalização\n"
                 "✓ Bloqueia o IP automaticamente\n"
                 "✓ Registra todas as ações",
                 bg='#16213e', fg='#00ff88', justify='left', font=('Arial', 11)).pack(pady=20, padx=20)
        
        history_frame = tk.LabelFrame(self, text="📜 HISTÓRICO DE CONTRA-ATAQUES", bg='#16213e', fg='#ff8800', font=('Arial', 12, 'bold'))
        history_frame.pack(fill='both', expand=True, padx=30, pady=10)
        
        top_frame = tk.Frame(history_frame, bg='#16213e')
        top_frame.pack(fill='x', padx=10, pady=5)
        
        self.clear_btn = tk.Button(top_frame, text="🗑️ LIMPAR HISTÓRICO", command=self.clear_history,
                                   bg='#ff4444', fg='white', font=('Arial', 10, 'bold'),
                                   padx=20, pady=5, cursor='hand2')
        self.clear_btn.pack(side='right')
        
        self.count_label = tk.Label(top_frame, text="Total de eventos: 0", bg='#16213e', fg='#888', font=('Arial', 10))
        self.count_label.pack(side='left')
        
        self.history_text = scrolledtext.ScrolledText(history_frame, bg='#0a0a1a', fg='#ff8800', 
                                                       font=('Courier', 10), height=18)
        self.history_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.add_history("📋 Sistema de contra-ataque automático inicializado")
        self.add_history("⚡ Aguardando detecção de ameaças...")
        
    def add_attack_event(self, event):
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        
        self.history_text.insert('end', f"\n{'='*50}\n")
        self.history_text.insert('end', f"[{ts}] 🎯 CONTRA-ATAQUE AUTOMÁTICO\n")
        self.history_text.insert('end', f"📍 IP Atacante: {event.get('ip', 'N/A')}\n")
        self.history_text.insert('end', f"⚠️ Tipo de Ameaça: {event.get('threat', 'N/A')}\n")
        for info in event.get('info', []):
            self.history_text.insert('end', f"   {info}\n")
        self.history_text.insert('end', f"✅ Ação: IP bloqueado automaticamente\n")
        self.history_text.insert('end', f"{'='*50}\n")
        self.history_text.see('end')
        
        lines = self.history_text.get('1.0', 'end').strip().split('\n')
        self.count_label.config(text=f"Total de eventos: {len([l for l in lines if '🎯' in l])}")
        
    def add_history(self, msg):
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        self.history_text.insert('end', f"[{ts}] {msg}\n")
        self.history_text.see('end')
        
        lines = self.history_text.get('1.0', 'end').strip().split('\n')
        self.count_label.config(text=f"Total de eventos: {len([l for l in lines if '🎯' in l])}")
        
    def clear_history(self):
        if messagebox.askyesno("Confirmar", "Limpar todo o histórico de contra-ataques?"):
            self.history_text.delete('1.0', 'end')
            self.add_history("📋 Histórico de contra-ataques limpo")
            self.add_history("⚡ Aguardando novas ameaças...")
            self.count_label.config(text="Total de eventos: 0")
            self.app.logs_tab.add_log("Histórico de contra-ataques limpo", "info")
