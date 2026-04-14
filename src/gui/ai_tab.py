import tkinter as tk
from tkinter import ttk
import threading
import time

class AITab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='#0a0a1a')
        self.app = app
        self.setup_ui()
        self.start_updates()
        
    def setup_ui(self):
        title_frame = tk.Frame(self, bg='#0a0a1a')
        title_frame.pack(fill='x', pady=20, padx=30)
        tk.Label(title_frame, text="🧠 INTELIGÊNCIA ARTIFICIAL", font=('Arial', 24, 'bold'),
                bg='#0a0a1a', fg='#00ff88').pack()
        
        # Cards
        cards_frame = tk.Frame(self, bg='#0a0a1a')
        cards_frame.pack(fill='x', padx=30, pady=10)
        
        # Isolation Forest
        c1 = tk.Frame(cards_frame, bg='#16213e', relief='ridge', bd=2)
        c1.pack(side='left', padx=10, pady=10, expand=True, fill='both')
        tk.Label(c1, text="🌲 ISOLATION FOREST", bg='#16213e', fg='#ff8800', font=('Arial', 12, 'bold')).pack(pady=(15,5))
        tk.Label(c1, text="Detecção de Anomalias", bg='#16213e', fg='#ccc', font=('Arial', 10)).pack()
        
        # Random Forest
        c2 = tk.Frame(cards_frame, bg='#16213e', relief='ridge', bd=2)
        c2.pack(side='left', padx=10, pady=10, expand=True, fill='both')
        tk.Label(c2, text="🌳 RANDOM FOREST", bg='#16213e', fg='#00ccff', font=('Arial', 12, 'bold')).pack(pady=(15,5))
        tk.Label(c2, text="Classificação de Ameaças", bg='#16213e', fg='#ccc', font=('Arial', 10)).pack()
        
        # Status
        status_frame = tk.Frame(self, bg='#16213e', relief='ridge', bd=2)
        status_frame.pack(fill='x', padx=30, pady=10)
        
        tk.Label(status_frame, text="📊 ANÁLISE EM TEMPO REAL", font=('Arial', 14, 'bold'),
                bg='#16213e', fg='#00ff88').pack(pady=10)
        
        self.status_text = tk.Text(status_frame, bg='#0a0a1a', fg='#00ff88', font=('Courier', 10), height=10)
        self.status_text.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Info
        info_frame = tk.Frame(self, bg='#16213e', relief='ridge', bd=2)
        info_frame.pack(fill='x', padx=30, pady=10)
        
        tk.Label(info_frame, text="ℹ️ INFORMAÇÕES", font=('Arial', 14, 'bold'),
                bg='#16213e', fg='#ff8800').pack(pady=10)
        
        self.info_text = tk.Text(info_frame, bg='#0a0a1a', fg='#ccc', font=('Courier', 10), height=8)
        self.info_text.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.update_ai_info()
        
    def update_ai_info(self):
        if self.app.defense_engine:
            info = self.app.defense_engine.get_ai_info()
            self.info_text.delete('1.0', 'end')
            self.info_text.insert('1.0', f"""
Detector: {info.get('anomaly_detector', 'N/A')}
Classificador: {info.get('threat_classifier', 'N/A')}
Status: {'TREINADO' if info.get('is_trained') else 'NÃO TREINADO'}
Features: {', '.join(info.get('features', []))}
Acurácia: {info.get('accuracy', 'N/A')}
            """)
        
    def start_updates(self):
        def update_loop():
            while True:
                if self.winfo_exists() and self.app.defense_engine and self.app.is_defense_active:
                    analysis = self.app.defense_engine.ai_engine.analyze_traffic()
                    if analysis:
                        self.status_text.delete('1.0', 'end')
                        if analysis.get('is_threat'):
                            self.status_text.insert('1.0', f"""
🔴 AMEAÇA DETECTADA!
{'='*35}
Tipo: {analysis.get('type', 'UNKNOWN')}
Confiança: {analysis.get('confidence', 0):.1f}%
Score: {analysis.get('anomaly_score', 0):.2f}
{'='*35}
✅ Ação: Bloqueio automático
                            """)
                        else:
                            self.status_text.insert('1.0', f"""
🟢 TRÁFEGO NORMAL
{'='*25}
Confiança: {analysis.get('confidence', 100):.1f}%
Score: {analysis.get('anomaly_score', 0):.2f}
{'='*25}
                            """)
                time.sleep(2)
        threading.Thread(target=update_loop, daemon=True).start()
