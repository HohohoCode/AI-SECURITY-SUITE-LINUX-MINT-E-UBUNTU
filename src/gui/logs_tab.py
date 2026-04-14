import tkinter as tk
from tkinter import scrolledtext, filedialog
from datetime import datetime

class LogsTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='#0a0a1a')
        self.app = app
        self.setup_ui()
        
    def setup_ui(self):
        tk.Label(self, text="📝 LOGS DO SISTEMA", font=('Arial', 24, 'bold'),
                bg='#0a0a1a', fg='#00ccff').pack(pady=20, padx=30)
        
        self.log_text = scrolledtext.ScrolledText(self, bg='#16213e', fg='#00ff88', font=('Courier', 10), height=25)
        self.log_text.pack(fill='both', expand=True, padx=30, pady=10)
        
        # Tags de cor
        self.log_text.tag_config("success", foreground="#00ff88")
        self.log_text.tag_config("alert", foreground="#ff4444")
        self.log_text.tag_config("warning", foreground="#ffaa00")
        self.log_text.tag_config("info", foreground="#ffffff")
        
        btn_frame = tk.Frame(self, bg='#0a0a1a')
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="🗑️ LIMPAR LOGS", command=self.clear_logs,
                 bg='#ff4444', fg='white', font=('Arial', 10, 'bold'), padx=20, pady=5, cursor='hand2').pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="💾 EXPORTAR LOGS", command=self.export_logs,
                 bg='#00ccff', fg='#0a0a1a', font=('Arial', 10, 'bold'), padx=20, pady=5, cursor='hand2').pack(side='left', padx=5)
        
        self.add_log("📋 Sistema de logs inicializado", "success")
        
    def add_log(self, msg, level="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        tag = level if level in ["success", "alert", "warning"] else "info"
        self.log_text.insert('end', f"[{timestamp}] {msg}\n", tag)
        self.log_text.see('end')
        
    def clear_logs(self):
        self.log_text.delete('1.0', 'end')
        self.add_log("Logs limpos", "success")
        
    def export_logs(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".log", filetypes=[("Log files", "*.log")])
        if file_path:
            with open(file_path, 'w') as f:
                f.write(self.log_text.get('1.0', 'end'))
            self.add_log(f"Logs exportados para {file_path}", "success")
