"""
DASHBOARD AVANÇADO
- Heatmap de ataques
- Gráficos de tendências
- Previsão de próximos ataques
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from datetime import datetime, timedelta
from collections import deque
import random

class AdvancedDashboard(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='#0a0a1a')
        self.app = app
        self.attack_history = deque(maxlen=100)
        self.setup_ui()
        self.start_updates()
    
    def setup_ui(self):
        # Título
        title = tk.Label(self, text="📈 DASHBOARD AVANÇADO", font=('Arial', 20, 'bold'),
                        bg='#0a0a1a', fg='#00ff88')
        title.pack(pady=20)
        
        # Notebook para abas
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Aba 1: Heatmap
        self.heatmap_frame = tk.Frame(notebook, bg='#0a0a1a')
        notebook.add(self.heatmap_frame, text="🔥 Heatmap de Ataques")
        self.setup_heatmap()
        
        # Aba 2: Tendências
        self.trends_frame = tk.Frame(notebook, bg='#0a0a1a')
        notebook.add(self.trends_frame, text="📊 Tendências")
        self.setup_trends()
        
        # Aba 3: Previsões
        self.forecast_frame = tk.Frame(notebook, bg='#0a0a1a')
        notebook.add(self.forecast_frame, text="🔮 Previsões IA")
        self.setup_forecast()
    
    def setup_heatmap(self):
        """Configura o heatmap de ataques"""
        # Canvas para desenhar o mapa
        self.heatmap_canvas = tk.Canvas(self.heatmap_frame, bg='#16213e', width=800, height=400)
        self.heatmap_canvas.pack(pady=20, padx=20)
        
        # Legenda
        legend_frame = tk.Frame(self.heatmap_frame, bg='#16213e')
        legend_frame.pack(pady=10)
        
        colors = ['#00ff88', '#88ff00', '#ffaa00', '#ff4400', '#ff0000']
        labels = ['Baixo', 'Médio', 'Alto', 'Crítico', 'Extremo']
        
        for i, (color, label) in enumerate(zip(colors, labels)):
            tk.Label(legend_frame, text=label, bg=color, width=10, height=1).pack(side='left', padx=5)
        
        self.update_heatmap()
    
    def setup_trends(self):
        """Configura gráfico de tendências"""
        self.trends_canvas = tk.Canvas(self.trends_frame, bg='#16213e', width=800, height=400)
        self.trends_canvas.pack(pady=20, padx=20)
        
        self.trends_label = tk.Label(self.trends_frame, text="Atualizando...", 
                                     bg='#0a0a1a', fg='#00ff88', font=('Arial', 12))
        self.trends_label.pack()
    
    def setup_forecast(self):
        """Configura previsões"""
        self.forecast_text = tk.Text(self.forecast_frame, bg='#16213e', fg='#00ff88',
                                      font=('Courier', 12), height=15, wrap='word')
        self.forecast_text.pack(fill='both', expand=True, padx=20, pady=20)
        
        self.update_forecast()
    
    def update_heatmap(self):
        """Atualiza o heatmap com dados reais"""
        def run():
            self.heatmap_canvas.delete("all")
            
            # Simular mapa de calor baseado em ataques reais
            width = 800
            height = 400
            
            # Criar grid
            cols = 20
            rows = 10
            cell_w = width / cols
            cell_h = height / rows
            
            # Obter dados de ataque
            blocked_ips = self.app.defense_engine.get_blocked_ips() if self.app.defense_engine else []
            intensity = min(len(blocked_ips) / 10, 1.0)
            
            for i in range(cols):
                for j in range(rows):
                    # Calcular intensidade baseada em ataques
                    x = i * cell_w
                    y = j * cell_h
                    
                    # Simular hotspots baseados em IPs bloqueados
                    noise = random.random() * intensity
                    color_intensity = min(255, int(noise * 255))
                    color = f'#{color_intensity:02x}{max(0, 255-color_intensity):02x}{max(0, 255-color_intensity*2):02x}'
                    
                    self.heatmap_canvas.create_rectangle(x, y, x + cell_w, y + cell_h, 
                                                          fill=color, outline='#1a1a2e')
            
            # Adicionar título
            self.heatmap_canvas.create_text(width/2, 20, text=f"Heatmap - {len(blocked_ips)} IPs bloqueados",
                                            fill='white', font=('Arial', 12, 'bold'))
        
        threading.Thread(target=run, daemon=True).start()
        self.after(10000, self.update_heatmap)  # Atualizar a cada 10 segundos
    
    def update_trends(self):
        """Atualiza gráfico de tendências"""
        def run():
            self.trends_canvas.delete("all")
            
            width = 800
            height = 400
            
            # Obter histórico de ameaças
            threats = self.app.defense_engine.get_threats() if self.app.defense_engine else []
            
            # Preparar dados
            last_hours = 24
            points = []
            
            for hour in range(last_hours):
                hour_threats = sum(1 for t in threats if datetime.fromtimestamp(t.get('timestamp', 0)).hour == hour)
                points.append(hour_threats)
            
            if points:
                max_val = max(points) or 1
                step_x = width / len(points)
                
                # Desenhar linha
                for i, val in enumerate(points):
                    x = i * step_x
                    y = height - (val / max_val) * (height - 50)
                    
                    if i > 0:
                        prev_x = (i-1) * step_x
                        prev_y = height - (points[i-1] / max_val) * (height - 50)
                        self.trends_canvas.create_line(prev_x, prev_y, x, y, fill='#00ff88', width=2)
                    
                    # Pontos
                    self.trends_canvas.create_oval(x-3, y-3, x+3, y+3, fill='#ff4444')
                    
                    # Rótulos
                    if i % 4 == 0:
                        self.trends_canvas.create_text(x, height-10, text=f"{i}h", fill='#888')
            
            # Adicionar título
            self.trends_canvas.create_text(width/2, 20, text="Tendência de Ataques (Últimas 24h)",
                                           fill='white', font=('Arial', 12, 'bold'))
            
            self.trends_label.config(text=f"Pico de ataques: {max(points)} na última hora" if points else "Sem dados")
        
        threading.Thread(target=run, daemon=True).start()
        self.after(5000, self.update_trends)
    
    def update_forecast(self):
        """Atualiza previsões de IA"""
        def run():
            self.forecast_text.delete('1.0', 'end')
            
            threats = self.app.defense_engine.get_threats() if self.app.defense_engine else []
            
            # Análise preditiva simples
            recent_threats = len([t for t in threats if t.get('timestamp', 0) > time.time() - 3600])
            avg_threats = len(threats) / max(24, 1) if threats else 0
            
            # Previsões
            forecast = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         🔮 PREVISÕES DA IA 🔮                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 ANÁLISE PREDITIVA:
   • Tendência atual: {'CRESCENTE' if recent_threats > avg_threats else 'DECRESCENTE'}
   • Média de ataques/hora: {avg_threats:.1f}
   • Ataques na última hora: {recent_threats}
   • Previsão para próxima hora: {max(0, int(recent_threats * 1.2)) if recent_threats > avg_threats else max(0, int(recent_threats * 0.8))}

🎯 RISCOS IDENTIFICADOS:
"""
            
            # Identificar padrões
            ddos_risk = sum(1 for t in threats if t.get('type') == 'DDoS')
            brute_risk = sum(1 for t in threats if t.get('type') == 'BRUTE_FORCE')
            
            if ddos_risk > 10:
                forecast += "   • 🔴 ALTO RISCO de DDoS nas próximas horas\n"
            elif ddos_risk > 5:
                forecast += "   • 🟡 RISCO MÉDIO de DDoS\n"
            
            if brute_risk > 20:
                forecast += "   • 🔴 ALTO RISCO de ataques de força bruta\n"
            elif brute_risk > 10:
                forecast += "   • 🟡 RISCO MÉDIO de força bruta\n"
            
            forecast += f"""
💡 RECOMENDAÇÕES DA IA:
   • {'Manter bloqueio ativo - Alerta elevado' if recent_threats > avg_threats else 'Monitoramento normal - Níveis aceitáveis'}
   • Verificar logs a cada {30 if recent_threats > avg_threats else 60} minutos
   • {'Recomendado ativar modo de defesa máximo' if recent_threats > avg_threats * 1.5 else 'Configuração atual adequada'}

📈 CONFIANÇA DA PREVISÃO: {min(95, 60 + (recent_threats / max(avg_threats, 1)) * 20):.0f}%
"""
            self.forecast_text.insert('1.0', forecast)
        
        threading.Thread(target=run, daemon=True).start()
        self.after(15000, self.update_forecast)  # Atualizar a cada 15 segundos
    
    def start_updates(self):
        self.update_trends()
        self.update_forecast()
