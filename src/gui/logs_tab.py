import tkinter as tk
from tkinter import scrolledtext, filedialog
from datetime import datetime

class LogsTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='#0a0a1a')
        self.app = app
        self.setup_ui()
    
    def setup_ui(self):
        tk.Label(self, text="📝 LOGS", font=('Arial', 24, 'bold'),
                bg='#0a0a1a', fg='#00ccff').pack(pady=20)
        
        self.text = scrolledtext.ScrolledText(self, bg='#16213e', fg='#00ff88', font=('Courier', 10), height=25)
        self.text.pack(fill='both', expand=True, padx=30, pady=10)
        
        btn_frame = tk.Frame(self, bg='#0a0a1a')
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="🗑️ LIMPAR", command=self.clear,
                 bg='#ff4444', fg='white', padx=20, pady=5, cursor='hand2').pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="💾 EXPORTAR", command=self.export,
                 bg='#00ccff', fg='#0a0a1a', padx=20, pady=5, cursor='hand2').pack(side='left', padx=5)
        
        self.add_log("📋 Sistema iniciado")
    
    def add_log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.text.insert('end', f"[{ts}] {msg}\n")
        self.text.see('end')
    
    def clear(self):
        self.text.delete('1.0', 'end')
        self.add_log("Logs limpos")
    
    def export(self):
        path = filedialog.asksaveasfilename(defaultextension=".log")
        if path:
            with open(path, 'w') as f:
                f.write(self.text.get('1.0', 'end'))
            self.add_log(f"Logs exportados para {path}")
