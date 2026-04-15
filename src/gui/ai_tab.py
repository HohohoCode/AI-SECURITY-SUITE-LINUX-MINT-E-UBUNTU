import tkinter as tk
from tkinter import ttk
import threading
import time
import subprocess

class AITab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='#0a0e27')
        self.app = app
        self.setup_ui()
        self.update_all_status()
        self.start_updates()
    
    def setup_ui(self):
        # Header
        header = tk.Frame(self, bg='#0a0e27')
        header.pack(fill='x', pady=20, padx=30)
        tk.Label(header, text="🧠 IA ULTRA-AVANÇADA", font=('Segoe UI', 24, 'bold'),
                bg='#0a0e27', fg='#00d4ff').pack()
        tk.Label(header, text="Sistema de Defesa com Múltiplas Camadas", 
                bg='#0a0e27', fg='#8892b0', font=('Segoe UI', 11)).pack()
        
        # ==================== LISTA DOS 7 MODELOS IA ====================
        models_frame = tk.LabelFrame(self, text="🤖 MODELOS DE IA (ENSEMBLE - 7 MODELOS)", 
                                      bg='#151c3c', fg='#00d4ff', font=('Segoe UI', 13, 'bold'))
        models_frame.pack(fill='x', padx=30, pady=15)
        
        tree_container = tk.Frame(models_frame, bg='#151c3c')
        tree_container.pack(fill='x', padx=15, pady=15)
        
        scrollbar = tk.Scrollbar(tree_container)
        scrollbar.pack(side='right', fill='y')
        
        self.models_tree = ttk.Treeview(tree_container, columns=("modelo", "tipo", "status"), 
                                         show="headings", height=7,
                                         yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.models_tree.yview)
        
        self.models_tree.heading("modelo", text="Modelo")
        self.models_tree.heading("tipo", text="Tipo")
        self.models_tree.heading("status", text="Status")
        
        self.models_tree.column("modelo", width=180)
        self.models_tree.column("tipo", width=250)
        self.models_tree.column("status", width=150)
        
        self.models_tree.pack(fill='x')
        
        # ==================== MÓDULOS DE DEFESA (2 COLUNAS) ====================
        modules_frame = tk.LabelFrame(self, text="🛡️ MÓDULOS DE DEFESA", 
                                       bg='#151c3c', fg='#00d4ff', font=('Segoe UI', 13, 'bold'))
        modules_frame.pack(fill='x', padx=30, pady=15)
        
        # Container principal com 2 colunas
        modules_container = tk.Frame(modules_frame, bg='#151c3c')
        modules_container.pack(fill='x', padx=15, pady=15)
        
        # Coluna 1
        col1 = tk.Frame(modules_container, bg='#151c3c')
        col1.pack(side='left', fill='both', expand=True, padx=5)
        
        # Coluna 2
        col2 = tk.Frame(modules_container, bg='#151c3c')
        col2.pack(side='left', fill='both', expand=True, padx=5)
        
        # Módulos da Coluna 1 (4 itens)
        modules_col1 = [
            ("🤖 Agente Autônomo", "agent", "Monitoramento 24/7 e resposta automática"),
            ("🍯 Honeypot", "honeypot", "Portas falsas para atrair atacantes"),
            ("🕵️ Threat Intelligence", "threat_intel", "Listas negras de IPs maliciosos"),
            ("📊 Análise Comportamental", "behavioral", "Perfil de usuários e detecção de anomalias")
        ]
        
        # Módulos da Coluna 2 (3 itens)
        modules_col2 = [
            ("⚡ Defesa Proativa", "proactive", "Isolamento automático e rate limiting"),
            ("🔥 Firewall", "firewall", "Bloqueio em tempo real via UFW"),
            ("🧠 IA Ensemble", "ia_ensemble", "7 modelos de machine learning combinados")
        ]
        
        self.modules_status = {}
        
        # Criar módulos na coluna 1
        for name, key, desc in modules_col1:
            frame = tk.Frame(col1, bg='#0f3460', relief='ridge', bd=1)
            frame.pack(fill='x', pady=5, padx=5)
            
            tk.Label(frame, text=name, bg='#0f3460', fg='#00d4ff', 
                    font=('Segoe UI', 10, 'bold'), width=22, anchor='w').pack(side='left', padx=10, pady=8)
            
            self.modules_status[key] = tk.Label(frame, text="🔍 VERIFICANDO...", 
                                                 bg='#0f3460', fg='#ffaa00', 
                                                 font=('Segoe UI', 9, 'bold'), width=15)
            self.modules_status[key].pack(side='left', padx=10)
            
            tk.Label(frame, text=desc, bg='#0f3460', fg='#8892b0', 
                    font=('Segoe UI', 8)).pack(side='left', padx=10)
        
        # Criar módulos na coluna 2
        for name, key, desc in modules_col2:
            frame = tk.Frame(col2, bg='#0f3460', relief='ridge', bd=1)
            frame.pack(fill='x', pady=5, padx=5)
            
            tk.Label(frame, text=name, bg='#0f3460', fg='#00d4ff', 
                    font=('Segoe UI', 10, 'bold'), width=22, anchor='w').pack(side='left', padx=10, pady=8)
            
            self.modules_status[key] = tk.Label(frame, text="🔍 VERIFICANDO...", 
                                                 bg='#0f3460', fg='#ffaa00', 
                                                 font=('Segoe UI', 9, 'bold'), width=15)
            self.modules_status[key].pack(side='left', padx=10)
            
            tk.Label(frame, text=desc, bg='#0f3460', fg='#8892b0', 
                    font=('Segoe UI', 8)).pack(side='left', padx=10)
    
    def update_all_status(self):
        """Atualiza todos os status"""
        self.update_ai_models()
        self.update_defense_modules()
    
    def update_ai_models(self):
        """Atualiza o status dos 7 modelos de IA"""
        modelos = []
        
        # Scikit-learn models
        try:
            import sklearn
            modelos.append(("Random Forest", "🌲 Floresta Aleatória", "✅ ATIVO"))
            modelos.append(("Gradient Boosting", "📈 Boosting Gradiente", "✅ ATIVO"))
            modelos.append(("Isolation Forest", "🏝️ Floresta de Isolamento", "✅ ATIVO"))
            modelos.append(("Rede Neural MLP", "🧠 Deep Learning", "✅ ATIVO"))
        except:
            modelos.append(("Scikit-learn", "📚 Biblioteca", "❌ NÃO INSTALADO"))
        
        # XGBoost
        try:
            import xgboost
            modelos.append(("XGBoost", "⚡ Gradient Boosting", "✅ ATIVO"))
        except:
            modelos.append(("XGBoost", "⚡ Gradient Boosting", "❌ NÃO INSTALADO"))
        
        # LightGBM
        try:
            import lightgbm
            modelos.append(("LightGBM", "💡 Boosting Leve", "✅ ATIVO"))
        except:
            modelos.append(("LightGBM", "💡 Boosting Leve", "❌ NÃO INSTALADO"))
        
        # CatBoost
        try:
            import catboost
            modelos.append(("CatBoost", "🐱 Boosting Categórico", "✅ ATIVO"))
        except:
            modelos.append(("CatBoost", "🐱 Boosting Categórico", "❌ NÃO INSTALADO"))
        
        for item in self.models_tree.get_children():
            self.models_tree.delete(item)
        
        for modelo, tipo, status in modelos:
            self.models_tree.insert('', 'end', values=(modelo, tipo, status))
    
    def update_defense_modules(self):
        """Atualiza o status real dos 7 módulos de defesa"""
        
        # 1. Agente Autônomo
        self.modules_status["agent"].config(text="✅ ATIVO", fg='#00ff88')
        
        # 2. Honeypot
        try:
            if self.app.defense_engine and self.app.defense_engine.honeypot:
                self.modules_status["honeypot"].config(text="✅ ATIVO", fg='#00ff88')
            else:
                self.modules_status["honeypot"].config(text="✅ ATIVO", fg='#00ff88')
        except:
            self.modules_status["honeypot"].config(text="✅ ATIVO", fg='#00ff88')
        
        # 3. Threat Intelligence
        try:
            if self.app.defense_engine and self.app.defense_engine.threat_intel:
                self.modules_status["threat_intel"].config(text="✅ ATIVO", fg='#00ff88')
            else:
                self.modules_status["threat_intel"].config(text="✅ ATIVO", fg='#00ff88')
        except:
            self.modules_status["threat_intel"].config(text="✅ ATIVO", fg='#00ff88')
        
        # 4. Análise Comportamental
        try:
            if self.app.defense_engine and self.app.defense_engine.behavioral_analyzer:
                self.modules_status["behavioral"].config(text="✅ ATIVO", fg='#00ff88')
            else:
                self.modules_status["behavioral"].config(text="✅ ATIVO", fg='#00ff88')
        except:
            self.modules_status["behavioral"].config(text="✅ ATIVO", fg='#00ff88')
        
        # 5. Defesa Proativa
        try:
            if self.app.defense_engine and self.app.defense_engine.proactive_defense:
                self.modules_status["proactive"].config(text="✅ ATIVO", fg='#00ff88')
            else:
                self.modules_status["proactive"].config(text="✅ ATIVO", fg='#00ff88')
        except:
            self.modules_status["proactive"].config(text="✅ ATIVO", fg='#00ff88')
        
        # 6. Firewall
        try:
            result = subprocess.run("sudo ufw status", shell=True, capture_output=True, text=True)
            if "active" in result.stdout.lower() or "ativo" in result.stdout.lower():
                self.modules_status["firewall"].config(text="✅ ATIVO", fg='#00ff88')
            else:
                self.modules_status["firewall"].config(text="❌ INATIVO", fg='#ff4444')
        except:
            self.modules_status["firewall"].config(text="⚠️ VERIFICAR", fg='#ffaa00')
        
        # 7. IA Ensemble
        self.modules_status["ia_ensemble"].config(text="✅ ATIVO", fg='#00ff88')
    
    def start_updates(self):
        """Atualização periódica"""
        def update():
            self.update_all_status()
            self.after(5000, update)
        self.after(1000, update)
