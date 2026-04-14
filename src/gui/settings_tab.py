import tkinter as tk

class SettingsTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='#0a0a1a')
        self.app = app
        self.setup_ui()
        
    def setup_ui(self):
        tk.Label(self, text="⚙️ CONFIGURAÇÕES", font=('Arial', 24, 'bold'),
                bg='#0a0a1a', fg='#00ff88').pack(pady=20, padx=30)
        
        main_frame = tk.Frame(self, bg='#16213e', relief='ridge', bd=2)
        main_frame.pack(fill='x', padx=30, pady=20)
        
        self.auto_block = tk.BooleanVar(value=self.app.settings.get("auto_block", True))
        tk.Checkbutton(main_frame, text="🚫 Bloqueio automático de IPs", variable=self.auto_block,
                      bg='#16213e', fg='white', selectcolor='#16213e', font=('Arial', 12)).pack(pady=15, padx=20, anchor='w')
        
        self.auto_counter = tk.BooleanVar(value=self.app.settings.get("auto_counter", True))
        tk.Checkbutton(main_frame, text="⚔️ Contra-ataque automático", variable=self.auto_counter,
                      bg='#16213e', fg='white', selectcolor='#16213e', font=('Arial', 12)).pack(pady=15, padx=20, anchor='w')
        
        tk.Label(main_frame, text="🎯 Sensibilidade da Detecção:", bg='#16213e', fg='white',
                font=('Arial', 12)).pack(pady=(20,5), anchor='w', padx=20)
        
        self.sensitivity = tk.Scale(main_frame, from_=0, to=100, orient='horizontal',
                                   bg='#16213e', fg='white', highlightbackground='#16213e',
                                   length=300)
        self.sensitivity.set(self.app.settings.get("sensitivity", 70))
        self.sensitivity.pack(padx=20, pady=(0,20))
        
        self.sens_label = tk.Label(main_frame, text="Médio (70%)", bg='#16213e', fg='#ccc')
        self.sens_label.pack(anchor='w', padx=20)
        self.sensitivity.configure(command=self.update_sens_label)
        
        tk.Button(main_frame, text="💾 SALVAR CONFIGURAÇÕES", command=self.save_settings,
                 bg='#00ff88', fg='#0a0a1a', font=('Arial', 12, 'bold'),
                 padx=30, pady=10, cursor='hand2').pack(pady=20)
        
        info_frame = tk.Frame(self, bg='#16213e', relief='ridge', bd=2)
        info_frame.pack(fill='x', padx=30, pady=10)
        
        tk.Label(info_frame, text="ℹ️ SISTEMA", font=('Arial', 14, 'bold'),
                bg='#16213e', fg='#00ff88').pack(pady=10)
        
        import sys
        info_text = f"""
        AI Security Suite Pro v3.0
        Linux Mint - Totalmente Automático
        
        Funcionalidades:
        • Monitoramento em tempo real
        • Detecção automática de ameaças
        • Bloqueio automático de IPs
        • Contra-ataque automático
        """
        
        tk.Label(info_frame, text=info_text, bg='#16213e', fg='#ccc', justify='left',
                font=('Courier', 10)).pack(pady=10, padx=20)
        
    def update_sens_label(self, value):
        val = int(value)
        if val < 30:
            text = f"Baixo ({val}%)"
        elif val < 70:
            text = f"Médio ({val}%)"
        else:
            text = f"Alto ({val}%)"
        self.sens_label.config(text=text)
        
    def save_settings(self):
        self.app.settings.set("auto_block", self.auto_block.get())
        self.app.settings.set("auto_counter", self.auto_counter.get())
        self.app.settings.set("sensitivity", self.sensitivity.get())
        if self.app.defense_engine:
            self.app.defense_engine.settings = self.app.settings
        self.app.logs_tab.add_log("Configurações salvas", "success")
