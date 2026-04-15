import tkinter as tk
from tkinter import ttk
import threading
import time

class AITab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='#0a0a1a')
        self.app = app
        self.last_scroll_position = 0
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
        tk.Label(title_frame, text="🧠 IA ULTRA-AVANÇADA + AGENTE AUTÔNOMO", font=('Arial', 22, 'bold'),
                bg='#0a0a1a', fg='#00ff88').pack()
        tk.Label(title_frame, text="Ensemble Learning com 7 Modelos | Agente de Defesa em Tempo Real", 
                bg='#0a0a1a', fg='#888', font=('Arial', 11)).pack()
        
        # ==================== SEÇÃO 1: MODELOS DE IA ====================
        models_section = tk.LabelFrame(self.inner_frame, text="🤖 MODELOS DE IA (ENSEMBLE)", 
                                        bg='#16213e', fg='#00ff88', font=('Arial', 14, 'bold'))
        models_section.pack(fill='x', padx=30, pady=15)
        
        # Cards principais
        cards_frame = tk.Frame(models_section, bg='#16213e')
        cards_frame.pack(fill='x', padx=15, pady=15)
        
        # Card 1 - Total de Modelos Ativos
        c1 = tk.Frame(cards_frame, bg='#0f3460', relief='ridge', bd=2, height=100)
        c1.pack(side='left', padx=10, pady=10, expand=True, fill='both')
        c1.pack_propagate(False)
        tk.Label(c1, text="🤖 MODELOS ATIVOS", bg='#0f3460', fg='#00ff88', font=('Arial', 11, 'bold')).pack(pady=(10,5))
        self.total_models_label = tk.Label(c1, text="0/7", bg='#0f3460', fg='#00ff88', font=('Arial', 28, 'bold'))
        self.total_models_label.pack(pady=(0,10))
        
        # Card 2 - Acurácia Estimada
        c2 = tk.Frame(cards_frame, bg='#0f3460', relief='ridge', bd=2, height=100)
        c2.pack(side='left', padx=10, pady=10, expand=True, fill='both')
        c2.pack_propagate(False)
        tk.Label(c2, text="🎯 ACURÁCIA ESTIMADA", bg='#0f3460', fg='#ff8800', font=('Arial', 11, 'bold')).pack(pady=(10,5))
        self.accuracy_label = tk.Label(c2, text="0%", bg='#0f3460', fg='#ff8800', font=('Arial', 28, 'bold'))
        self.accuracy_label.pack(pady=(0,10))
        
        # Card 3 - Features
        c3 = tk.Frame(cards_frame, bg='#0f3460', relief='ridge', bd=2, height=100)
        c3.pack(side='left', padx=10, pady=10, expand=True, fill='both')
        c3.pack_propagate(False)
        tk.Label(c3, text="📊 FEATURES", bg='#0f3460', fg='#00ccff', font=('Arial', 11, 'bold')).pack(pady=(10,5))
        self.features_label = tk.Label(c3, text="12", bg='#0f3460', fg='#00ccff', font=('Arial', 28, 'bold'))
        self.features_label.pack(pady=(0,10))
        
        # Lista de Modelos
        tree_container = tk.Frame(models_section, bg='#16213e')
        tree_container.pack(fill='x', padx=15, pady=10)
        
        scrollbar_y = tk.Scrollbar(tree_container)
        scrollbar_y.pack(side='right', fill='y')
        
        self.models_tree = ttk.Treeview(tree_container, columns=("modelo", "tipo", "peso", "status"), 
                                         show="headings", height=7,
                                         yscrollcommand=scrollbar_y.set)
        scrollbar_y.config(command=self.models_tree.yview)
        
        self.models_tree.heading("modelo", text="Modelo")
        self.models_tree.heading("tipo", text="Tipo")
        self.models_tree.heading("peso", text="Peso")
        self.models_tree.heading("status", text="Status")
        
        self.models_tree.column("modelo", width=130)
        self.models_tree.column("tipo", width=250)
        self.models_tree.column("peso", width=70)
        self.models_tree.column("status", width=200)
        
        self.models_tree.pack(fill='x')
        
        # ==================== SEÇÃO 2: AGENTE AUTÔNOMO ====================
        agent_section = tk.LabelFrame(self.inner_frame, text="🤖 AGENTE DE DEFESA AUTÔNOMO", 
                                       bg='#16213e', fg='#ff8800', font=('Arial', 14, 'bold'))
        agent_section.pack(fill='x', padx=30, pady=15)
        
        # Cards do Agente
        agent_cards = tk.Frame(agent_section, bg='#16213e')
        agent_cards.pack(fill='x', padx=15, pady=15)
        
        # Card - Ameaças Analisadas
        a1 = tk.Frame(agent_cards, bg='#0f3460', relief='ridge', bd=2, height=90)
        a1.pack(side='left', padx=10, pady=10, expand=True, fill='both')
        a1.pack_propagate(False)
        tk.Label(a1, text="📊 AMEAÇAS ANALISADAS", bg='#0f3460', fg='#00ff88', font=('Arial', 10, 'bold')).pack(pady=(8,0))
        self.threats_analyzed_label = tk.Label(a1, text="0", bg='#0f3460', fg='#00ff88', font=('Arial', 24, 'bold'))
        self.threats_analyzed_label.pack()
        
        # Card - IPs Bloqueados
        a2 = tk.Frame(agent_cards, bg='#0f3460', relief='ridge', bd=2, height=90)
        a2.pack(side='left', padx=10, pady=10, expand=True, fill='both')
        a2.pack_propagate(False)
        tk.Label(a2, text="🚫 IPs BLOQUEADOS", bg='#0f3460', fg='#ff4444', font=('Arial', 10, 'bold')).pack(pady=(8,0))
        self.agent_blocked_label = tk.Label(a2, text="0", bg='#0f3460', fg='#ff4444', font=('Arial', 24, 'bold'))
        self.agent_blocked_label.pack()
        
        # Card - Tempo Médio de Resposta
        a3 = tk.Frame(agent_cards, bg='#0f3460', relief='ridge', bd=2, height=90)
        a3.pack(side='left', padx=10, pady=10, expand=True, fill='both')
        a3.pack_propagate(False)
        tk.Label(a3, text="⚡ TEMPO DE RESPOSTA", bg='#0f3460', fg='#00ccff', font=('Arial', 10, 'bold')).pack(pady=(8,0))
        self.response_time_label = tk.Label(a3, text="0ms", bg='#0f3460', fg='#00ccff', font=('Arial', 24, 'bold'))
        self.response_time_label.pack()
        
        # Card - Tempo Ativo
        a4 = tk.Frame(agent_cards, bg='#0f3460', relief='ridge', bd=2, height=90)
        a4.pack(side='left', padx=10, pady=10, expand=True, fill='both')
        a4.pack_propagate(False)
        tk.Label(a4, text="⏱️ TEMPO ATIVO", bg='#0f3460', fg='#aa66ff', font=('Arial', 10, 'bold')).pack(pady=(8,0))
        self.agent_uptime_label = tk.Label(a4, text="0h", bg='#0f3460', fg='#aa66ff', font=('Arial', 24, 'bold'))
        self.agent_uptime_label.pack()
        
        # Limiares adaptativos
        thresholds_frame = tk.Frame(agent_section, bg='#16213e')
        thresholds_frame.pack(fill='x', padx=15, pady=10)
        
        tk.Label(thresholds_frame, text="📈 LIMIARES ADAPTATIVOS", bg='#16213e', fg='#ff8800', 
                font=('Arial', 11, 'bold')).pack(anchor='w')
        
        thresholds_grid = tk.Frame(thresholds_frame, bg='#16213e')
        thresholds_grid.pack(fill='x', pady=5)
        
        self.thresholds_labels = {}
        thresholds_data = [
            ("DDoS (conexões/10s)", "ddos", "100"),
            ("Brute Force (tentativas/60s)", "bruteforce", "10"),
            ("Port Scan (portas/10s)", "portscan", "20"),
            ("Confiança Mínima (%)", "confidence", "70")
        ]
        
        for i, (label, key, default) in enumerate(thresholds_data):
            row = i // 2
            col = i % 2
            frame = tk.Frame(thresholds_grid, bg='#0f3460', relief='ridge', bd=1)
            frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            thresholds_grid.grid_columnconfigure(col, weight=1)
            
            tk.Label(frame, text=label, bg='#0f3460', fg='#ccc', font=('Arial', 9)).pack(pady=(5,0))
            self.thresholds_labels[key] = tk.Label(frame, text=default, bg='#0f3460', fg='#00ff88', 
                                                    font=('Arial', 14, 'bold'))
            self.thresholds_labels[key].pack(pady=(0,5))
        
        # ==================== SEÇÃO 3: ANÁLISE EM TEMPO REAL (MAIOR AINDA) ====================
        realtime_frame = tk.LabelFrame(self.inner_frame, text="📈 ANÁLISE EM TEMPO REAL", 
                                        bg='#16213e', fg='#00ff88', font=('Arial', 14, 'bold'))
        realtime_frame.pack(fill='both', expand=True, padx=30, pady=15)
        
        # Texto MAIOR para análise em tempo real
        self.realtime_text = tk.Text(realtime_frame, bg='#0a0a1a', fg='#00ff88', 
                                      font=('Courier', 11), height=50, wrap='word')
        self.realtime_text.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Barra de rolagem para o texto
        realtime_scrollbar = tk.Scrollbar(realtime_frame, orient='vertical', command=self.realtime_text.yview)
        realtime_scrollbar.pack(side='right', fill='y')
        self.realtime_text.config(yscrollcommand=realtime_scrollbar.set)
        
        self.update_ai_info()
        
    def _on_frame_configure(self, event):
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox('all'))
    
    def _on_canvas_configure(self, event):
        self.main_canvas.itemconfig(1, width=event.width)
        
    def update_ai_info(self):
        if self.app.defense_engine:
            # Informações dos Modelos IA
            ai_info = self.app.defense_engine.get_ai_info()
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
            
            # Informações do Agente Autônomo
            agent_stats = self.app.defense_engine.get_agent_stats()
            if agent_stats:
                autonomous = agent_stats.get('autonomous', {})
                self.threats_analyzed_label.config(text=str(autonomous.get('total_threats_analyzed', 0)))
                self.agent_blocked_label.config(text=str(autonomous.get('total_blocks', 0)))
                
                response_time = autonomous.get('avg_response_time', 0)
                self.response_time_label.config(text=f"{response_time:.0f}ms" if response_time > 0 else "0ms")
                
                uptime = autonomous.get('uptime', 0)
                hours = int(uptime // 3600)
                minutes = int((uptime % 3600) // 60)
                self.agent_uptime_label.config(text=f"{hours}h {minutes}m")
                
                # Atualizar limiares
                thresholds = autonomous.get('active_thresholds', {})
                if thresholds:
                    self.thresholds_labels['ddos'].config(text=str(thresholds.get('ddos_connections', 100)))
                    self.thresholds_labels['bruteforce'].config(text=str(thresholds.get('bruteforce_attempts', 10)))
                    self.thresholds_labels['portscan'].config(text=str(thresholds.get('port_scan_ports', 20)))
                    self.thresholds_labels['confidence'].config(text=str(thresholds.get('confidence_threshold', 70)))
        
    def start_updates(self):
        def update_loop():
            while True:
                if self.winfo_exists() and self.app.defense_engine and self.app.is_defense_active:
                    # Salvar posição atual da rolagem ANTES de atualizar
                    current_pos = self.realtime_text.yview()
                    
                    # Obter análise dos modelos IA
                    analysis = self.app.defense_engine.ai_engine.get_real_time_analysis()
                    
                    # Obter estatísticas do agente
                    agent_stats = self.app.defense_engine.get_agent_stats()
                    
                    # Atualizar o texto
                    self.realtime_text.delete('1.0', 'end')
                    
                    if analysis:
                        if analysis.get('is_threat'):
                            self.realtime_text.insert('1.0', f"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                         🔴 AMEAÇA DETECTADA PELA IA 🔴                                                                          ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

📊 TIPO DE AMEAÇA: {analysis.get('type', 'UNKNOWN')}
🎯 CONFIANÇA: {analysis.get('confidence', 0):.1f}%
🤖 MODELOS UTILIZADOS: {analysis.get('models_used', 0)}/7

📈 VOTAÇÃO DOS MODELOS:
{self._format_votes(analysis.get('votes', {}))}

✅ AÇÃO: IP bloqueado automaticamente pelo Agente Autônomo

⚡ ENSEMBLE: Votação ponderada com {analysis.get('models_used', 0)} modelos ativos
                            """)
                        else:
                            self.realtime_text.insert('1.0', f"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                         🟢 TRÁFEGO NORMAL 🟢                                                                                    ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

📊 STATUS: Nenhuma ameaça detectada
🎯 CONFIANÇA: {analysis.get('confidence', 100):.1f}%
🤖 MODELOS ATIVOS: {analysis.get('models_used', 0)}/7

📈 VOTAÇÃO:
{self._format_votes(analysis.get('votes', {}))}

✅ Sistema protegido por {analysis.get('models_used', 0)} modelos de IA em ensemble
                            """)
                    
                    # Adicionar informações do Agente
                    if agent_stats:
                        autonomous = agent_stats.get('autonomous', {})
                        honeypot = agent_stats.get('honeypot', {})
                        threat_intel = agent_stats.get('threat_intel', {})
                        behavioral = agent_stats.get('behavioral', {})
                        proactive = agent_stats.get('proactive', {})
                        
                        self.realtime_text.insert('end', f"""

╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                         🤖 STATUS DO AGENTE AUTÔNOMO 🤖                                                                           ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

📊 Total de ameaças analisadas: {autonomous.get('total_threats_analyzed', 0)}
🚫 Total de IPs bloqueados: {autonomous.get('total_blocks', 0)}
⚡ Tempo médio de resposta: {autonomous.get('avg_response_time', 0):.0f}ms
⏱️ Tempo ativo: {int(autonomous.get('uptime', 0) // 3600)}h {int((autonomous.get('uptime', 0) % 3600) // 60)}m
🔒 IPs na cache de bloqueio: {autonomous.get('blocked_ips_count', 0)}
📈 Histórico de ameaças: {autonomous.get('threats_in_history', 0)}

🎯 LIMIARES ADAPTATIVOS ATUAIS:
   • DDoS: {autonomous.get('active_thresholds', {}).get('ddos_connections', 100)} conexões/10s
   • Brute Force: {autonomous.get('active_thresholds', {}).get('bruteforce_attempts', 10)} tentativas/60s
   • Port Scan: {autonomous.get('active_thresholds', {}).get('port_scan_ports', 20)} portas/10s
   • Confiança mínima: {autonomous.get('active_thresholds', {}).get('confidence_threshold', 70)}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🍯 HONEYPOT: {honeypot.get('total_attacks', 0)} ataques registrados | {honeypot.get('unique_attackers', 0)} atacantes únicos

🕵️ THREAT INTELLIGENCE: {threat_intel.get('total_malicious_ips', 0)} IPs maliciosos na lista negra

📊 ANÁLISE COMPORTAMENTAL: {behavioral.get('total_users', 0)} usuários monitorados | {behavioral.get('anomalies_detected', 0)} anomalias

🛡️ DEFESA PROATIVA: {proactive.get('isolated_machines', 0)} máquinas isoladas | {proactive.get('rate_limited_ips', 0)} IPs com rate limit

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
                    
                    # RESTAURAR a posição da rolagem após atualizar
                    self.realtime_text.yview_moveto(current_pos[0])
                    
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
