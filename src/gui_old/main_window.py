import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.settings import Settings
from core.defense_engine import DefenseEngine
from core.counter_attack import CounterAttack

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🛡️ AI Security Suite Pro - Linux Mint")
        self.root.geometry("1300x800")
        self.root.configure(bg='#1a1a2e')
        
        # Configurar estilo
        self.setup_styles()
        
        self.settings = Settings()
        self.defense_engine = DefenseEngine(self.settings, self.handle_event)
        self.counter_attack = CounterAttack(self.settings, self.handle_event)
        self.is_defense_active = False
        
        self.setup_ui()
        self.start_status_updates()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background="#2d2d3d", foreground="white", fieldbackground="#2d2d3d")
        style.configure("Treeview.Heading", background="#1a1a2e", foreground="white", font=('Arial', 10, 'bold'))
        
    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg='#0f3460', height=70)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text="🛡️ AI SECURITY SUITE PRO", font=('Arial', 20, 'bold'), 
                bg='#0f3460', fg='#00ff88').pack(side='left', padx=30, pady=15)
        
        self.status_indicator = tk.Label(header, text="● DEFESA INATIVA", 
                                         font=('Arial', 12, 'bold'), bg='#0f3460', fg='#ff4444')
        self.status_indicator.pack(side='right', padx=30)
        
        self.defense_btn = tk.Button(header, text="🔴 ATIVAR DEFESA", command=self.toggle_defense,
                                    bg='#00ff88', fg='#1a1a2e', font=('Arial', 12, 'bold'),
                                    padx=20, pady=8, cursor='hand2', relief='flat')
        self.defense_btn.pack(side='right', padx=20)
        
        # Container principal
        main_container = tk.Frame(self.root, bg='#1a1a2e')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Sidebar
        sidebar = tk.Frame(main_container, bg='#16213e', width=220)
        sidebar.pack(side='left', fill='y', padx=(0,10))
        sidebar.pack_propagate(False)
        
        # Stats no sidebar
        tk.Label(sidebar, text="📊 ESTATÍSTICAS", font=('Arial', 12, 'bold'),
                bg='#16213e', fg='#00ff88').pack(pady=(20,10))
        
        self.stats_labels = {}
        stats = [("Ameaças", "0"), ("Bloqueios", "0"), ("Ativo", "00:00:00")]
        for label, default in stats:
            frame = tk.Frame(sidebar, bg='#0f3460', relief='ridge', bd=1)
            frame.pack(fill='x', padx=15, pady=5)
            tk.Label(frame, text=label, bg='#0f3460', fg='#ccc', font=('Arial', 10)).pack(pady=(5,0))
            self.stats_labels[label] = tk.Label(frame, text=default, bg='#0f3460', fg='#00ff88', 
                                                font=('Arial', 16, 'bold'))
            self.stats_labels[label].pack(pady=(0,5))
        
        # Navegação
        tk.Label(sidebar, text="📁 NAVEGAÇÃO", font=('Arial', 12, 'bold'),
                bg='#16213e', fg='#00ff88').pack(pady=(20,10))
        
        nav_buttons = [
            ("🏠 Dashboard", self.show_dashboard),
            ("⚠️ Ameaças", self.show_threats),
            ("🔥 Firewall", self.show_firewall),
            ("⚔️ Contra-Ataque", self.show_counter),
            ("📝 Logs", self.show_logs),
            ("⚙️ Configurações", self.show_settings)
        ]
        
        for text, cmd in nav_buttons:
            btn = tk.Button(sidebar, text=text, command=cmd, bg='#0f3460', fg='white',
                           font=('Arial', 11), padx=10, pady=8, relief='flat',
                           cursor='hand2', anchor='w')
            btn.pack(fill='x', padx=15, pady=3)
        
        # Content area
        self.content = tk.Frame(main_container, bg='#1a1a2e')
        self.content.pack(side='left', fill='both', expand=True)
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="✅ Sistema pronto | Clique em ATIVAR DEFESA para começar",
                                  bg='#0f3460', fg='#ccc', anchor='w', font=('Arial', 9))
        self.status_bar.pack(fill='x')
        
        # Criar abas
        self.dashboard = DashboardTab(self.content, self)
        self.threats_tab = ThreatsTab(self.content, self)
        self.firewall_tab = FirewallTab(self.content, self)
        self.counter_tab = CounterTab(self.content, self)
        self.logs_tab = LogsTab(self.content, self)
        self.settings_tab = SettingsTab(self.content, self)
        
        self.show_dashboard()
        
    def handle_event(self, event):
        self.root.after(0, lambda: self.process_event(event))
        
    def process_event(self, event):
        if event.get("type") == "log":
            self.logs_tab.add_log(event.get("message", ""), event.get("level", "info"))
            self.status_bar.config(text=event.get("message", "")[:100])
        elif event.get("type") == "counter_attack":
            self.counter_tab.add_attack_event(event)
            self.logs_tab.add_log(f"⚔️ Contra-ataque concluído contra {event.get('ip')}", "success")
        elif "source" in event or "source_ip" in event:
            self.threats_tab.add_threat(event)
            
    def toggle_defense(self):
        if not self.is_defense_active:
            self.defense_engine.start()
            self.is_defense_active = True
            self.defense_btn.config(text="🟢 DEFESA ATIVA", bg='#ff4444')
            self.status_indicator.config(text="● DEFESA ATIVA", fg='#00ff88')
            self.logs_tab.add_log("🚀 Sistema de defesa ATIVADO", "success")
        else:
            self.defense_engine.stop()
            self.is_defense_active = False
            self.defense_btn.config(text="🔴 ATIVAR DEFESA", bg='#00ff88')
            self.status_indicator.config(text="● DEFESA INATIVA", fg='#ff4444')
            self.logs_tab.add_log("🛑 Sistema de defesa DESATIVADO", "warning")
            
    def start_status_updates(self):
        def update():
            while True:
                if self.is_defense_active and self.defense_engine:
                    stats = self.defense_engine.get_stats()
                    self.root.after(0, lambda: self.update_stats_display(stats))
                time.sleep(2)
        threading.Thread(target=update, daemon=True).start()
        
    def update_stats_display(self, stats):
        self.stats_labels["Ameaças"].config(text=str(stats.get("threats_detected", 0)))
        self.stats_labels["Bloqueios"].config(text=str(stats.get("threats_blocked", 0)))
        uptime = stats.get("uptime", 0)
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        seconds = int(uptime % 60)
        self.stats_labels["Ativo"].config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        self.dashboard.update_stats(stats)
        
    def show_dashboard(self): self.hide_all(); self.dashboard.pack(fill='both', expand=True)
    def show_threats(self): self.hide_all(); self.threats_tab.pack(fill='both', expand=True)
    def show_firewall(self): self.hide_all(); self.firewall_tab.pack(fill='both', expand=True)
    def show_counter(self): self.hide_all(); self.counter_tab.pack(fill='both', expand=True)
    def show_logs(self): self.hide_all(); self.logs_tab.pack(fill='both', expand=True)
    def show_settings(self): self.hide_all(); self.settings_tab.pack(fill='both', expand=True)
    
    def hide_all(self):
        for w in [self.dashboard, self.threats_tab, self.firewall_tab, 
                  self.counter_tab, self.logs_tab, self.settings_tab]:
            w.pack_forget()
            
    def run(self):
        self.root.mainloop()


class DashboardTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='#1a1a2e')
        self.app = app
        self.setup_ui()
        
    def setup_ui(self):
        tk.Label(self, text="📊 DASHBOARD", font=('Arial', 24, 'bold'),
                bg='#1a1a2e', fg='#00ff88').pack(pady=20)
        
        # Cards
        cards_frame = tk.Frame(self, bg='#1a1a2e')
        cards_frame.pack(pady=20, padx=20, fill='x')
        
        self.cards = {}
        cards_data = [
            ("🛡️ Ameaças Detectadas", "threats", "#ff4444"),
            ("🚫 IPs Bloqueados", "blocked", "#ff8800"),
            ("📦 Pacotes/s", "packets", "#00ff88"),
            ("🔗 Conexões", "connections", "#00ccff")
        ]
        
        for i, (label, key, color) in enumerate(cards_data):
            card = tk.Frame(cards_frame, bg='#16213e', relief='ridge', bd=2)
            card.grid(row=0, column=i, padx=10, pady=10, sticky='nsew')
            cards_frame.grid_columnconfigure(i, weight=1)
            
            tk.Label(card, text=label, bg='#16213e', fg=color, font=('Arial', 12)).pack(pady=(15,5))
            self.cards[key] = tk.Label(card, text="0", bg='#16213e', fg=color, font=('Arial', 32, 'bold'))
            self.cards[key].pack(pady=(0,15))
            
        # Status do sistema
        status_frame = tk.Frame(self, bg='#16213e', relief='ridge', bd=2)
        status_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(status_frame, text="🖥️ STATUS DO SISTEMA", font=('Arial', 14, 'bold'),
                bg='#16213e', fg='#00ff88').pack(pady=10)
        
        self.system_status = {}
        status_items = [("Firewall", "Verificando..."), ("Defesa", "Inativa"), ("Monitoramento", "Parado")]
        
        for label, default in status_items:
            frame = tk.Frame(status_frame, bg='#16213e')
            frame.pack(fill='x', pady=5, padx=20)
            tk.Label(frame, text=f"{label}:", bg='#16213e', fg='#ccc', width=15, anchor='w').pack(side='left')
            self.system_status[label] = tk.Label(frame, text=default, bg='#16213e', fg='#00ff88', anchor='w')
            self.system_status[label].pack(side='left')
            
        # Botão de atualizar firewall
        tk.Button(status_frame, text="🔄 Atualizar Status do Firewall", command=self.update_firewall_status,
                 bg='#0f3460', fg='white', cursor='hand2').pack(pady=10)
        
        self.update_firewall_status()
        
    def update_stats(self, stats):
        self.cards["threats"].config(text=str(stats.get("threats_detected", 0)))
        self.cards["blocked"].config(text=str(stats.get("threats_blocked", 0)))
        self.cards["packets"].config(text=str(stats.get("packets_analyzed", 0)))
        self.cards["connections"].config(text=str(stats.get("active_connections", 0)))
        
        # Atualizar status da defesa
        if self.app.is_defense_active:
            self.system_status["Defesa"].config(text="Ativa", fg='#00ff88')
            self.system_status["Monitoramento"].config(text="Em execução", fg='#00ff88')
        else:
            self.system_status["Defesa"].config(text="Inativa", fg='#ff4444')
            self.system_status["Monitoramento"].config(text="Parado", fg='#ff4444')
            
    def update_firewall_status(self):
        import subprocess
        try:
            result = subprocess.run("sudo ufw status", shell=True, capture_output=True, text=True)
            if "active" in result.stdout:
                self.system_status["Firewall"].config(text="Ativo", fg='#00ff88')
            else:
                self.system_status["Firewall"].config(text="Inativo", fg='#ff4444')
        except:
            self.system_status["Firewall"].config(text="Erro", fg='#ff4444')


class ThreatsTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='#1a1a2e')
        self.app = app
        self.setup_ui()
        
    def setup_ui(self):
        tk.Label(self, text="⚠️ LISTA DE AMEAÇAS", font=('Arial', 24, 'bold'),
                bg='#1a1a2e', fg='#ff4444').pack(pady=20)
        
        # Treeview
        frame = tk.Frame(self, bg='#1a1a2e')
        frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        scroll_y = ttk.Scrollbar(frame)
        scroll_y.pack(side='right', fill='y')
        
        self.tree = ttk.Treeview(frame, columns=("time", "type", "source", "level", "action"), 
                                  show="headings", yscrollcommand=scroll_y.set, height=15)
        scroll_y.config(command=self.tree.yview)
        
        self.tree.heading("time", text="Data/Hora")
        self.tree.heading("type", text="Tipo")
        self.tree.heading("source", text="Origem")
        self.tree.heading("level", text="Nível")
        self.tree.heading("action", text="Ação")
        
        self.tree.column("time", width=150)
        self.tree.column("type", width=120)
        self.tree.column("source", width=150)
        self.tree.column("level", width=80)
        self.tree.column("action", width=100)
        
        self.tree.pack(fill='both', expand=True)
        
        # Botões
        btn_frame = tk.Frame(self, bg='#1a1a2e')
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="🗑️ Limpar Histórico", command=self.clear_threats,
                 bg='#ff4444', fg='white', padx=20, pady=5, cursor='hand2').pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="📊 Exportar Relatório", command=self.export_report,
                 bg='#00ccff', fg='white', padx=20, pady=5, cursor='hand2').pack(side='left', padx=5)
        
    def add_threat(self, threat):
        time_str = datetime.fromtimestamp(threat.get("timestamp", time.time())).strftime("%Y-%m-%d %H:%M:%S")
        level = threat.get("level", "medium").upper()
        
        # Cor por nível
        tag = "high" if level in ["HIGH", "CRITICAL"] else "medium"
        self.tree.tag_configure("high", foreground="#ff4444")
        self.tree.tag_configure("medium", foreground="#ffaa00")
        
        self.tree.insert("", 0, values=(
            time_str,
            threat.get("type", "Unknown"),
            threat.get("source", threat.get("source_ip", "N/A")),
            level,
            "Bloqueado" if threat.get("action") != "pending" else "Registrado"
        ), tags=(tag,))
        
    def clear_threats(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.app.logs_tab.add_log("Histórico de ameaças limpo", "info")
        
    def export_report(self):
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'w') as f:
                f.write("RELATÓRIO DE AMEAÇAS - AI SECURITY SUITE\n")
                f.write("=" * 60 + "\n\n")
                for item in self.tree.get_children():
                    values = self.tree.item(item)['values']
                    f.write(f"Data: {values[0]} | Tipo: {values[1]} | Origem: {values[2]} | Nível: {values[3]}\n")
            self.app.logs_tab.add_log(f"Relatório exportado: {file_path}", "success")


class FirewallTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='#1a1a2e')
        self.app = app
        self.setup_ui()
        self.refresh()
        
    def setup_ui(self):
        tk.Label(self, text="🔥 GERENCIADOR DE FIREWALL", font=('Arial', 24, 'bold'),
                bg='#1a1a2e', fg='#ff8800').pack(pady=20)
        
        # Status
        self.status_frame = tk.Frame(self, bg='#16213e', relief='ridge', bd=2)
        self.status_frame.pack(fill='x', padx=20, pady=10)
        
        self.status_label = tk.Label(self.status_frame, text="Status: Verificando...", 
                                     font=('Arial', 16, 'bold'), bg='#16213e')
        self.status_label.pack(pady=20)
        
        # Botões de controle
        btn_frame = tk.Frame(self.status_frame, bg='#16213e')
        btn_frame.pack(pady=10)
        
        self.enable_btn = tk.Button(btn_frame, text="🟢 ATIVAR FIREWALL", command=self.enable_firewall,
                                   bg='#00ff88', fg='#1a1a2e', font=('Arial', 11, 'bold'),
                                   padx=20, pady=8, cursor='hand2')
        self.enable_btn.pack(side='left', padx=10)
        
        self.disable_btn = tk.Button(btn_frame, text="🔴 DESATIVAR FIREWALL", command=self.disable_firewall,
                                    bg='#ff4444', fg='white', font=('Arial', 11, 'bold'),
                                    padx=20, pady=8, cursor='hand2')
        self.disable_btn.pack(side='left', padx=10)
        
        self.refresh_btn = tk.Button(btn_frame, text="🔄 ATUALIZAR", command=self.refresh,
                                    bg='#0f3460', fg='white', font=('Arial', 11, 'bold'),
                                    padx=20, pady=8, cursor='hand2')
        self.refresh_btn.pack(side='left', padx=10)
        
        # Regras do firewall
        tk.Label(self, text="📋 REGRAS DO FIREWALL", font=('Arial', 14, 'bold'),
                bg='#1a1a2e', fg='#00ff88').pack(pady=(20,5))
        
        self.rules_text = scrolledtext.ScrolledText(self, bg='#16213e', fg='#00ff88',
                                                    font=('Courier', 10), height=12)
        self.rules_text.pack(fill='both', expand=True, padx=20, pady=10)
        
        # IPs bloqueados
        tk.Label(self, text="🚫 IPs BLOQUEADOS", font=('Arial', 14, 'bold'),
                bg='#1a1a2e', fg='#ff4444').pack(pady=(10,5))
        
        self.blocked_frame = tk.Frame(self, bg='#1a1a2e')
        self.blocked_frame.pack(fill='x', padx=20, pady=10)
        
        self.blocked_listbox = tk.Listbox(self.blocked_frame, bg='#16213e', fg='#00ff88',
                                          font=('Courier', 10), height=5)
        self.blocked_listbox.pack(side='left', fill='both', expand=True)
        
        self.unblock_btn = tk.Button(self.blocked_frame, text="🔓 DESBLOQUEAR", command=self.unblock_selected,
                                    bg='#ff8800', fg='white', padx=15, pady=5, cursor='hand2')
        self.unblock_btn.pack(side='right', padx=10)
        
    def refresh(self):
        import subprocess
        try:
            # Verificar status
            result = subprocess.run("sudo ufw status", shell=True, capture_output=True, text=True)
            if "Status: active" in result.stdout:
                self.status_label.config(text="✅ Status: ATIVO", fg='#00ff88')
                self.enable_btn.config(state='disabled')
                self.disable_btn.config(state='normal')
            else:
                self.status_label.config(text="❌ Status: INATIVO", fg='#ff4444')
                self.enable_btn.config(state='normal')
                self.disable_btn.config(state='disabled')
                
            # Mostrar regras
            rules = subprocess.run("sudo ufw status numbered", shell=True, capture_output=True, text=True)
            self.rules_text.delete('1.0', 'end')
            self.rules_text.insert('1.0', rules.stdout if rules.stdout else "Nenhuma regra configurada")
            
            # Mostrar IPs bloqueados
            self.blocked_listbox.delete(0, 'end')
            if self.app.defense_engine:
                for ip in self.app.defense_engine.get_blocked_ips():
                    self.blocked_listbox.insert('end', ip)
                    
            self.app.logs_tab.add_log("Status do firewall atualizado", "info")
        except Exception as e:
            self.status_label.config(text=f"⚠️ Erro: {e}", fg='#ff4444')
            
    def enable_firewall(self):
        import subprocess
        def run():
            subprocess.run("sudo ufw --force enable", shell=True)
            self.refresh()
            self.app.logs_tab.add_log("🔥 Firewall ATIVADO", "success")
        threading.Thread(target=run, daemon=True).start()
        
    def disable_firewall(self):
        import subprocess
        def run():
            subprocess.run("sudo ufw disable", shell=True)
            self.refresh()
            self.app.logs_tab.add_log("🔥 Firewall DESATIVADO", "warning")
        threading.Thread(target=run, daemon=True).start()
        
    def unblock_selected(self):
        selection = self.blocked_listbox.curselection()
        if selection and self.app.defense_engine:
            ip = self.blocked_listbox.get(selection[0])
            if self.app.defense_engine.unblock_ip(ip):
                self.refresh()
                self.app.logs_tab.add_log(f"🔓 IP {ip} desbloqueado", "success")


class CounterTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='#1a1a2e')
        self.app = app
        self.setup_ui()
        
    def setup_ui(self):
        tk.Label(self, text="⚔️ CONTRA-ATAQUE AUTOMÁTICO", font=('Arial', 24, 'bold'),
                bg='#1a1a2e', fg='#00ff88').pack(pady=20)
        
        # Informação
        info_frame = tk.Frame(self, bg='#16213e', relief='ridge', bd=2)
        info_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(info_frame, text="🤖 O contra-ataque é AUTOMÁTICO quando uma ameaça é detectada\n"
                 "O sistema irá:\n"
                 "1. Identificar o IP do invasor\n"
                 "2. Coletar informações (WHOIS, Geolocalização)\n"
                 "3. Bloquear o IP automaticamente\n"
                 "4. Registrar todas as ações",
                 bg='#16213e', fg='#ccc', font=('Arial', 11), justify='left').pack(pady=20, padx=20)
        
        # Histórico de ataques
        tk.Label(self, text="📜 HISTÓRICO DE CONTRA-ATAQUES", font=('Arial', 14, 'bold'),
                bg='#1a1a2e', fg='#00ff88').pack(pady=(20,5))
        
        self.history_text = scrolledtext.ScrolledText(self, bg='#16213e', fg='#00ff88',
                                                      font=('Courier', 10), height=15)
        self.history_text.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Investigação manual
        tk.Label(self, text="🔍 INVESTIGAÇÃO MANUAL", font=('Arial', 14, 'bold'),
                bg='#1a1a2e', fg='#00ccff').pack(pady=(10,5))
        
        manual_frame = tk.Frame(self, bg='#1a1a2e')
        manual_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(manual_frame, text="IP:", bg='#1a1a2e', fg='white', font=('Arial', 12)).pack(side='left', padx=5)
        self.ip_entry = tk.Entry(manual_frame, width=25, bg='#16213e', fg='white', font=('Arial', 12))
        self.ip_entry.pack(side='left', padx=5)
        
        tk.Button(manual_frame, text="🔍 INVESTIGAR", command=self.manual_investigate,
                 bg='#00ccff', fg='#1a1a2e', font=('Arial', 11, 'bold'),
                 padx=20, pady=5, cursor='hand2').pack(side='left', padx=5)
        
        tk.Button(manual_frame, text="🚫 BLOQUEAR IP", command=self.manual_block,
                 bg='#ff4444', fg='white', font=('Arial', 11, 'bold'),
                 padx=20, pady=5, cursor='hand2').pack(side='left', padx=5)
        
    def add_attack_event(self, event):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history_text.insert('end', f"\n{'='*50}\n")
        self.history_text.insert('end', f"[{timestamp}] 🎯 CONTRA-ATAQUE\n")
        self.history_text.insert('end', f"IP: {event.get('ip', 'N/A')}\n")
        self.history_text.insert('end', f"Ameaça: {event.get('threat', 'N/A')}\n")
        
        for info in event.get('info', []):
            self.history_text.insert('end', f"{info}\n")
            
        self.history_text.insert('end', f"{'='*50}\n")
        self.history_text.see('end')
        
    def manual_investigate(self):
        ip = self.ip_entry.get().strip()
        if ip:
            def run():
                result = self.app.counter_attack.investigate_ip(ip)
                self.history_text.insert('end', f"\n{'='*50}\n")
                self.history_text.insert('end', f"🔍 INVESTIGAÇÃO MANUAL - {ip}\n")
                self.history_text.insert('end', f"📍 Localização: {result.get('geolocation', {}).get('country', 'N/A')}\n")
                self.history_text.insert('end', f"🔓 Portas abertas: {[p['port'] for p in result.get('open_ports', [])]}\n")
                self.history_text.insert('end', f"🌐 Reverse DNS: {result.get('reverse_dns', 'N/A')}\n")
                self.history_text.insert('end', f"{'='*50}\n")
                self.history_text.see('end')
                self.app.logs_tab.add_log(f"Investigação manual de {ip} concluída", "info")
            threading.Thread(target=run, daemon=True).start()
            
    def manual_block(self):
        ip = self.ip_entry.get().strip()
        if ip and self.app.defense_engine:
            self.app.defense_engine._block_ip(ip, "Bloqueio manual")
            self.history_text.insert('end', f"🚫 IP {ip} bloqueado manualmente\n")
            self.app.logs_tab.add_log(f"IP {ip} bloqueado manualmente", "alert")


class LogsTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='#1a1a2e')
        self.app = app
        self.setup_ui()
        
    def setup_ui(self):
        tk.Label(self, text="📝 LOGS DO SISTEMA", font=('Arial', 24, 'bold'),
                bg='#1a1a2e', fg='#00ccff').pack(pady=20)
        
        self.log_text = scrolledtext.ScrolledText(self, bg='#16213e', fg='#00ff88',
                                                  font=('Courier', 10), height=25)
        self.log_text.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Configurar tags de cor
        self.log_text.tag_config("success", foreground="#00ff88")
        self.log_text.tag_config("alert", foreground="#ff4444")
        self.log_text.tag_config("warning", foreground="#ffaa00")
        self.log_text.tag_config("error", foreground="#ff4444")
        
        btn_frame = tk.Frame(self, bg='#1a1a2e')
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="🗑️ LIMPAR LOGS", command=self.clear_logs,
                 bg='#ff4444', fg='white', padx=20, pady=5, cursor='hand2').pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="💾 EXPORTAR LOGS", command=self.export_logs,
                 bg='#00ccff', fg='#1a1a2e', padx=20, pady=5, cursor='hand2').pack(side='left', padx=5)
        
        self.add_log("📋 Sistema de logs inicializado", "success")
        
    def add_log(self, message, level="info"):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        tag = None
        if level in ["success", "alert", "warning", "error"]:
            tag = level
            
        self.log_text.insert('end', f"[{timestamp}] {message}\n", tag)
        self.log_text.see('end')
        
    def clear_logs(self):
        self.log_text.delete('1.0', 'end')
        self.add_log("Logs limpos", "success")
        
    def export_logs(self):
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(defaultextension=".log", filetypes=[("Log files", "*.log")])
        if file_path:
            with open(file_path, 'w') as f:
                f.write(self.log_text.get('1.0', 'end'))
            self.add_log(f"Logs exportados para {file_path}", "success")


class SettingsTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='#1a1a2e')
        self.app = app
        self.setup_ui()
        
    def setup_ui(self):
        tk.Label(self, text="⚙️ CONFIGURAÇÕES", font=('Arial', 24, 'bold'),
                bg='#1a1a2e', fg='#00ff88').pack(pady=20)
        
        # Configurações
        settings_frame = tk.Frame(self, bg='#16213e', relief='ridge', bd=2)
        settings_frame.pack(fill='x', padx=20, pady=10)
        
        # Auto block
        self.auto_block = tk.BooleanVar(value=self.app.settings.get("auto_block", True))
        tk.Checkbutton(settings_frame, text="Bloqueio automático de IPs", variable=self.auto_block,
                      bg='#16213e', fg='white', selectcolor='#16213e', font=('Arial', 11)).pack(pady=10, padx=20, anchor='w')
        
        # Auto counter
        self.auto_counter = tk.BooleanVar(value=self.app.settings.get("auto_counter", True))
        tk.Checkbutton(settings_frame, text="Contra-ataque automático", variable=self.auto_counter,
                      bg='#16213e', fg='white', selectcolor='#16213e', font=('Arial', 11)).pack(pady=10, padx=20, anchor='w')
        
        # Sensibilidade
        tk.Label(settings_frame, text="Sensibilidade da Detecção:", bg='#16213e', fg='white',
                font=('Arial', 11)).pack(pady=(20,5), anchor='w', padx=20)
        
        self.sensitivity = tk.Scale(settings_frame, from_=0, to=100, orient='horizontal',
                                   bg='#16213e', fg='white', highlightbackground='#16213e',
                                   length=300)
        self.sensitivity.set(self.app.settings.get("sensitivity", 70))
        self.sensitivity.pack(padx=20, pady=(0,20))
        
        # Scan interval
        tk.Label(settings_frame, text="Intervalo de Escaneamento (segundos):", bg='#16213e', fg='white',
                font=('Arial', 11)).pack(pady=(10,5), anchor='w', padx=20)
        
        self.scan_interval = tk.Scale(settings_frame, from_=1, to=10, orient='horizontal',
                                     bg='#16213e', fg='white', highlightbackground='#16213e',
                                     length=300)
        self.scan_interval.set(self.app.settings.get("scan_interval", 3))
        self.scan_interval.pack(padx=20, pady=(0,20))
        
        # Block duration
        tk.Label(settings_frame, text="Duração do Bloqueio (minutos):", bg='#16213e', fg='white',
                font=('Arial', 11)).pack(pady=(10,5), anchor='w', padx=20)
        
        self.block_duration = tk.Scale(settings_frame, from_=5, to=1440, orient='horizontal',
                                      bg='#16213e', fg='white', highlightbackground='#16213e',
                                      length=300)
        self.block_duration.set(self.app.settings.get("block_duration", 3600) / 60)
        self.block_duration.pack(padx=20, pady=(0,20))
        
        # Botão salvar
        tk.Button(settings_frame, text="💾 SALVAR CONFIGURAÇÕES", command=self.save_settings,
                 bg='#00ff88', fg='#1a1a2e', font=('Arial', 12, 'bold'),
                 padx=30, pady=10, cursor='hand2').pack(pady=20)
        
        # Informações
        info_frame = tk.Frame(self, bg='#16213e', relief='ridge', bd=2)
        info_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(info_frame, text="ℹ️ INFORMAÇÕES DO SISTEMA", font=('Arial', 14, 'bold'),
                bg='#16213e', fg='#00ff88').pack(pady=10)
        
        info_text = f"""
        AI Security Suite Pro v3.0
        Sistema: Linux Mint
        Python: {sys.version.split()[0]}
        
        Funcionalidades:
        • Monitoramento de rede em tempo real
        • Detecção automática de ameaças
        • Bloqueio de IPs via UFW/iptables
        • Contra-ataque automático com OSINT
        • Geolocalização de invasores
        • Logs detalhados
        """
        
        tk.Label(info_frame, text=info_text, bg='#16213e', fg='#ccc', justify='left',
                font=('Courier', 10)).pack(pady=10, padx=20)
        
    def save_settings(self):
        self.app.settings.set("auto_block", self.auto_block.get())
        self.app.settings.set("auto_counter", self.auto_counter.get())
        self.app.settings.set("sensitivity", self.sensitivity.get())
        self.app.settings.set("scan_interval", self.scan_interval.get())
        self.app.settings.set("block_duration", self.block_duration.get() * 60)
        
        if self.app.defense_engine:
            self.app.defense_engine.settings = self.app.settings
            
        self.app.logs_tab.add_log("Configurações salvas com sucesso", "success")
