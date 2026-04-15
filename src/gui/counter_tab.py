import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime
import time

class CounterTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='#0a0e27')
        self.app = app
        self.setup_ui()
        self.start_updates()
    
    def setup_ui(self):
        tk.Label(self, text="⚔️ CONTRA-ATAQUES", font=('Segoe UI', 24, 'bold'),
                bg='#0a0e27', fg='#00ccff').pack(pady=20)
        
        frame = tk.Frame(self, bg='#151c3c', relief='flat', bd=2)
        frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        top = tk.Frame(frame, bg='#151c3c')
        top.pack(fill='x', padx=10, pady=10)
        
        self.clear_btn = tk.Button(top, text="🗑️ LIMPAR", command=self.clear_history,
                                   bg='#ff4444', fg='white', font=('Segoe UI', 10, 'bold'),
                                   padx=20, pady=5, cursor='hand2')
        self.clear_btn.pack(side='right')
        
        self.count_label = tk.Label(top, text="Total: 0", bg='#151c3c', fg='#00ff88', font=('Segoe UI', 10, 'bold'))
        self.count_label.pack(side='left')
        
        self.text = scrolledtext.ScrolledText(frame, bg='#0a0e27', fg='#ff8800', font=('Courier', 10), height=18)
        self.text.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.add_history("📋 Sistema inicializado")
    
    def add_attack_event(self, event):
        ts = datetime.now().strftime("%H:%M:%S")
        self.text.insert('end', f"\n{'='*50}\n")
        self.text.insert('end', f"[{ts}] 🎯 CONTRA-ATAQUE\n")
        self.text.insert('end', f"📍 IP: {event.get('ip', 'N/A')}\n")
        self.text.insert('end', f"⚠️ Ameaça: {event.get('threat', 'N/A')}\n")
        for info in event.get('info', []):
            self.text.insert('end', f"   {info}\n")
        self.text.insert('end', f"{'='*50}\n")
        self.text.see('end')
        self.update_count()
    
    def add_history(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.text.insert('end', f"[{ts}] {msg}\n")
        self.text.see('end')
        self.update_count()
    
    def update_count(self):
        count = self.text.get('1.0', 'end').count('🎯')
        self.count_label.config(text=f"Total: {count}")
    
    def clear_history(self):
        if messagebox.askyesno("Confirmar", "Limpar histórico?"):
            self.text.delete('1.0', 'end')
            self.add_history("📋 Histórico limpo")
    
    def start_updates(self):
        def refresh():
            if self.app.defense_engine:
                attacks = self.app.defense_engine.get_counter_attacks()
                current = self.text.get('1.0', 'end')
                for attack in attacks[:5]:
                    if attack.get('ip') not in current:
                        self.add_attack_event(attack)
            self.after(3000, refresh)
        self.after(1000, refresh)
