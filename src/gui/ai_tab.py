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
        # Criar um canvas com scrollbar para toda a aba
        self.main_canvas = tk.Canvas(self, bg='#0a0a1a', highlightthickness=0)
        self.main_scrollbar = tk.Scrollbar(self, orient='vertical', command=self.main_canvas.yview)
        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)
        
        self.main_scrollbar.pack(side='right', fill='y')
        self.main_canvas.pack(side='left', fill='both', expand=True)
        
        # Frame interno que vai conter todo o conteúdo
        self.inner_frame = tk.Frame(self.main_canvas, bg='#0a0a1a')
        self.main_canvas.create_window((0, 0), window=self.inner_frame, anchor='nw', width=self.main_canvas.winfo_width())
        
        # Configurar para redimensionar
        self.inner_frame.bind('<Configure>', self._on_frame_configure)
        self.main_canvas.bind('<Configure>', self._on_canvas_configure)
        
        # Título
        title_frame = tk.Frame(self.inner_frame, bg='#0a0a1a')
        title_frame.pack(fill='x', pady=20, padx=30)
        tk.Label(title_frame, text="🧠 IA ULTRA-AVANÇADA", font=('Arial', 26, 'bold'),
                bg='#0a0a1a', fg='#00ff88').pack()
        tk.Label(title_frame, text="Ensemble Learning com 7 Modelos de IA | Votação Ponderada", 
                bg='#0a0a1a', fg='#888', font=('Arial', 12)).pack()
        
        # Cards principais (3 colunas)
        cards_frame = tk.Frame(self.inner_frame, bg='#0a0a1a')
        cards_frame.pack(fill='x', padx=30, pady=20)
        
        # Card 1 - Total de Modelos Ativos
        c1 = tk.Frame(cards_frame, bg='#16213e', relief='ridge', bd=2, height=120)
        c1.pack(side='left', padx=15, pady=10, expand=True, fill='both')
        c1.pack_propagate(False)
        tk.Label(c1, text="🤖 MODELOS ATIVOS", bg='#16213e', fg='#00ff88', font=('Arial', 12, 'bold')).pack(pady=(15,5))
        self.total_models_label = tk.Label(c1, text="0/7", bg='#16213e', fg='#00ff88', font=('Arial', 32, 'bold'))
        self.total_models_label.pack(pady=(0,15))
        
        # Card 2 - Acurácia Estimada
        c2 = tk.Frame(cards_frame, bg='#16213e', relief='ridge', bd=2, height=120)
        c2.pack(side='left', padx=15, pady=10, expand=True, fill='both')
        c2.pack_propagate(False)
        tk.Label(c2, text="🎯 ACURÁCIA ESTIMADA", bg='#16213e', fg='#ff8800', font=('Arial', 12, 'bold')).pack(pady=(15,5))
        self.accuracy_label = tk.Label(c2, text="0%", bg='#16213e', fg='#ff8800', font=('Arial', 32, 'bold'))
        self.accuracy_label.pack(pady=(0,15))
        
        # Card 3 - Features
        c3 = tk.Frame(cards_frame, bg='#16213e', relief='ridge', bd=2, height=120)
        c3.pack(side='left', padx=15, pady=10, expand=True, fill='both')
        c3.pack_propagate(False)
        tk.Label(c3, text="📊 FEATURES ANALISADAS", bg='#16213e', fg='#00ccff', font=('Arial', 12, 'bold')).pack(pady=(15,5))
        self.features_label = tk.Label(c3, text="12", bg='#16213e', fg='#00ccff', font=('Arial', 32, 'bold'))
        self.features_label.pack(pady=(0,15))
        
        # Lista de Modelos (expandida)
        models_frame = tk.LabelFrame(self.inner_frame, text="🤖 MODELOS DE IA (ENSEMBLE DE 7)", 
                                      bg='#16213e', fg='#00ff88', font=('Arial', 14, 'bold'))
        models_frame.pack(fill='x', padx=30, pady=15)
        
        # Criar Treeview com altura maior
        tree_container = tk.Frame(models_frame, bg='#16213e')
        tree_container.pack(fill='x', padx=15, pady=15)
        
        scrollbar_y = tk.Scrollbar(tree_container)
        scrollbar_y.pack(side='right', fill='y')
        
        scrollbar_x = tk.Scrollbar(tree_container, orient='horizontal')
        scrollbar_x.pack(side='bottom', fill='x')
        
        self.models_tree = ttk.Treeview(tree_container, columns=("modelo", "tipo", "peso", "status"), 
                                         show="headings", height=8,
                                         yscrollcommand=scrollbar_y.set,
                                         xscrollcommand=scrollbar_x.set)
        scrollbar_y.config(command=self.models_tree.yview)
        scrollbar_x.config(command=self.models_tree.xview)
        
        self.models_tree.heading("modelo", text="Modelo")
        self.models_tree.heading("tipo", text="Tipo")
        self.models_tree.heading("peso", text="Peso")
        self.models_tree.heading("status", text="Status")
        
        self.models_tree.column("modelo", width=130)
        self.models_tree.column("tipo", width=250)
        self.models_tree.column("peso", width=70)
        self.models_tree.column("status", width=250)
        
        self.models_tree.pack(fill='x')
        
        # Features detalhadas (expandido)
        features_frame = tk.LabelFrame(self.inner_frame, text="📊 FEATURES ANALISADAS EM TEMPO REAL", 
                                        bg='#16213e', fg='#00ccff', font=('Arial', 14, 'bold'))
        features_frame.pack(fill='x', padx=30, pady=15)
        
        self.features_text = tk.Text(features_frame, bg='#0a0a1a', fg='#00ff88', 
                                      font=('Courier', 11), height=8, wrap='word')
        self.features_text.pack(fill='x', padx=15, pady=15)
        
        # Análise em tempo real (expandido)
        realtime_frame = tk.LabelFrame(self.inner_frame, text="📈 ANÁLISE EM TEMPO REAL", 
                                        bg='#16213e', fg='#ff8800', font=('Arial', 14, 'bold'))
        realtime_frame.pack(fill='both', expand=True, padx=30, pady=15)
        
        self.realtime_text = tk.Text(realtime_frame, bg='#0a0a1a', fg='#00ff88', 
                                      font=('Courier', 11), height=15, wrap='word')
        self.realtime_text.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Legenda (expandida)
        legend_frame = tk.LabelFrame(self.inner_frame, text="📖 LEGENDA DOS MODELOS", 
                                      bg='#16213e', fg='#00ff88', font=('Arial', 14, 'bold'))
        legend_frame.pack(fill='x', padx=30, pady=15)
        
        legend_text = """
        🌲 Random Forest: 200 árvores de decisão | Alta precisão e robustez
        📈 Gradient Boosting: 150 estimadores | Aprendizado sequencial adaptativo
        🏝️ Isolation Forest: Detecção de anomalias | Isola outliers do padrão normal
        🧠 Rede Neural MLP: 4 camadas ocultas (128/64/32/16) | Deep Learning avançado
        ⚡ XGBoost: Gradient boosting otimizado | Alta performance e velocidade
        💡 LightGBM: Baseado em árvores | Rápido, eficiente e baixo consumo
        🐱 CatBoost: Tratamento automático de categorias | Robusto contra overfitting
        """
        
        tk.Label(legend_frame, text=legend_text, bg='#16213e', fg='#ccc', 
                font=('Courier', 10), justify='left').pack(pady=15, padx=25, anchor='w')
        
        # Aviso sobre modelos opcionais
        warning_frame = tk.Frame(self.inner_frame, bg='#16213e', relief='ridge', bd=2)
        warning_frame.pack(fill='x', padx=30, pady=15)
        
        tk.Label(warning_frame, text="💡 DICA: Para ativar todos os 7 modelos, instale as bibliotecas adicionais:", 
                bg='#16213e', fg='#ffaa00', font=('Arial', 11)).pack(pady=8)
        tk.Label(warning_frame, text="pip3 install xgboost lightgbm catboost --break-system-packages", 
                bg='#16213e', fg='#00ff88', font=('Courier', 11)).pack(pady=5)
        
        self.update_ai_info()
        
    def _on_frame_configure(self, event):
        """Atualiza a região de scroll quando o frame interno muda de tamanho"""
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox('all'))
    
    def _on_canvas_configure(self, event):
        """Redimensiona o frame interno quando o canvas muda de tamanho"""
        self.main_canvas.itemconfig(1, width=event.width)
        
    def update_ai_info(self):
        if self.app.defense_engine:
            ai_info = self.app.defense_engine.get_ai_info()
            
            # Atualizar cards
            self.total_models_label.config(text=f"{ai_info.get('total_models', 0)}/{ai_info.get('total_possible', 7)}")
            self.accuracy_label.config(text=ai_info.get('accuracy_estimate', 'N/A'))
            self.features_label.config(text=str(ai_info.get('features_count', 0)))
            
            # Atualizar lista de modelos
            for item in self.models_tree.get_children():
                self.models_tree.delete(item)
            
            for model in ai_info.get('models', []):
                status = model.get('status', 'N/A')
                if 'Ativo' in status:
                    status_display = "✅ " + status
                else:
                    status_display = "❌ " + status
                    
                self.models_tree.insert('', 'end', values=(
                    model.get('name', 'N/A'),
                    model.get('type', 'N/A'),
                    f"{model.get('weight', 0)}x",
                    status_display
                ))
            
            # Atualizar features
            self.features_text.delete('1.0', 'end')
            features = ai_info.get('features_list', [])
            
            # Criar uma tabela bonita para as features
            features_text = "╔" + "═" * 58 + "╗\n"
            features_text += "║ " + " │ ".join(f"{f:^12}" for f in features[:6]) + " ║\n"
            features_text += "╠" + "═" * 58 + "╣\n"
            features_text += "║ " + " │ ".join(f"{f:^12}" for f in features[6:]) + " ║\n"
            features_text += "╚" + "═" * 58 + "╝\n"
            self.features_text.insert('1.0', features_text)
        
    def start_updates(self):
        def update_loop():
            while True:
                if self.winfo_exists() and self.app.defense_engine and self.app.is_defense_active:
                    analysis = self.app.defense_engine.ai_engine.get_real_time_analysis()
                    if analysis:
                        self.realtime_text.delete('1.0', 'end')
                        
                        if analysis.get('is_threat'):
                            self.realtime_text.insert('1.0', f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                              🔴 AMEAÇA DETECTADA 🔴                           ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 TIPO DE AMEAÇA: {analysis.get('type', 'UNKNOWN')}
🎯 CONFIANÇA: {analysis.get('confidence', 0):.1f}%
🤖 MODELOS UTILIZADOS: {analysis.get('models_used', 0)}/7

📈 VOTAÇÃO DOS MODELOS:
{self._format_votes(analysis.get('votes', {}))}

✅ AÇÃO: IP bloqueado automaticamente no firewall

⚡ ENSEMBLE: Votação ponderada com {analysis.get('models_used', 0)} modelos ativos
                            """)
                        else:
                            self.realtime_text.insert('1.0', f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                              🟢 TRÁFEGO NORMAL 🟢                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 STATUS: Nenhuma ameaça detectada
🎯 CONFIANÇA: {analysis.get('confidence', 100):.1f}%
🤖 MODELOS ATIVOS: {analysis.get('models_used', 0)}/7

📈 VOTAÇÃO:
{self._format_votes(analysis.get('votes', {}))}

✅ Sistema protegido por {analysis.get('models_used', 0)} modelos de IA em ensemble
                            """)
                time.sleep(2)
        threading.Thread(target=update_loop, daemon=True).start()
    
    def _format_votes(self, votes):
        if not votes:
            return "   Nenhum voto registrado"
        
        lines = []
        for threat, weight in votes.items():
            bar_length = int(weight / 4)
            bar = "█" * bar_length + "░" * (25 - bar_length)
            lines.append(f"   {threat:16} : [{bar}] {weight:.1f}")
        return "\n".join(lines)
