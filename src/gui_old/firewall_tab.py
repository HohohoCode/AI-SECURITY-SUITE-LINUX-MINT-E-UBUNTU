import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import threading
import time

class FirewallTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='#1a1a2e')
        self.app = app
        self.firewall_status = None  # None = desconhecido, True = ativo, False = inativo
        self.setup_ui()
        self.refresh_status()
        
    def setup_ui(self):
        # Título
        tk.Label(self, text="🔥 GERENCIADOR DE FIREWALL", font=('Arial', 24, 'bold'),
                bg='#1a1a2e', fg='#ff8800').pack(pady=20)
        
        # Card principal
        main_card = tk.Frame(self, bg='#16213e', relief='ridge', bd=2)
        main_card.pack(fill='x', padx=20, pady=10)
        
        # Status com interruptor
        status_frame = tk.Frame(main_card, bg='#16213e')
        status_frame.pack(pady=20, padx=20, fill='x')
        
        # Label de status
        self.status_label = tk.Label(status_frame, text="FIREWALL", 
                                     font=('Arial', 18, 'bold'), bg='#16213e')
        self.status_label.pack(side='left', padx=(0, 20))
        
        # Interruptor (Toggle Switch)
        self.switch_frame = tk.Frame(status_frame, bg='#16213e', width=80, height=35)
        self.switch_frame.pack(side='left')
        self.switch_frame.pack_propagate(False)
        
        # Criar interruptor personalizado
        self.switch_canvas = tk.Canvas(self.switch_frame, width=80, height=35, 
                                        bg='#16213e', highlightthickness=0)
        self.switch_canvas.pack()
        
        # Desenhar o interruptor
        self.switch_bg = self.switch_canvas.create_rectangle(5, 5, 75, 30, 
                                                              fill='#555', outline='', 
                                                              cornerradius=15)
        self.switch_button = self.switch_canvas.create_oval(8, 8, 28, 28, 
                                                             fill='white', outline='')
        
        # Texto do interruptor
        self.switch_text = self.switch_canvas.create_text(55, 20, text="OFF", 
                                                           fill='white', font=('Arial', 10, 'bold'))
        
        # Bind do clique
        self.switch_canvas.tag_bind(self.switch_bg, '<Button-1>', self.toggle_firewall)
        self.switch_canvas.tag_bind(self.switch_button, '<Button-1>', self.toggle_firewall)
        
        # Texto de status detalhado
        self.detail_label = tk.Label(main_card, text="Verificando status...", 
                                     font=('Arial', 12), bg='#16213e', fg='#ccc')
        self.detail_label.pack(pady=(0, 20))
        
        # Frame de informações
        info_frame = tk.Frame(main_card, bg='#16213e')
        info_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Estatísticas do firewall
        tk.Label(info_frame, text="📊 ESTATÍSTICAS", font=('Arial', 12, 'bold'),
                bg='#16213e', fg='#00ff88').pack(anchor='w', pady=(0, 10))
        
        stats_grid = tk.Frame(info_frame, bg='#16213e')
        stats_grid.pack(fill='x')
        
        self.stats_labels = {}
        stats_items = [("Regras ativas", "0"), ("IPs bloqueados", "0"), ("Pacotes bloqueados", "0")]
        
        for i, (label, default) in enumerate(stats_items):
            frame = tk.Frame(stats_grid, bg='#0f3460', relief='ridge', bd=1)
            frame.grid(row=0, column=i, padx=5, pady=5, sticky='nsew')
            stats_grid.grid_columnconfigure(i, weight=1)
            
            tk.Label(frame, text=label, bg='#0f3460', fg='#ccc', font=('Arial', 10)).pack(pady=(5,0))
            self.stats_labels[label] = tk.Label(frame, text=default, bg='#0f3460', 
                                                 fg='#00ff88', font=('Arial', 16, 'bold'))
            self.stats_labels[label].pack(pady=(0,5))
        
        # Regras do firewall
        tk.Label(self, text="📋 REGRAS DO FIREWALL", font=('Arial', 14, 'bold'),
                bg='#1a1a2e', fg='#00ff88').pack(pady=(20,5))
        
        self.rules_text = scrolledtext.ScrolledText(self, bg='#16213e', fg='#00ff88',
                                                    font=('Courier', 10), height=10)
        self.rules_text.pack(fill='both', expand=True, padx=20, pady=10)
        
        # IPs bloqueados
        tk.Label(self, text="🚫 IPs BLOQUEADOS PELA IA", font=('Arial', 14, 'bold'),
                bg='#1a1a2e', fg='#ff4444').pack(pady=(10,5))
        
        blocked_frame = tk.Frame(self, bg='#1a1a2e')
        blocked_frame.pack(fill='x', padx=20, pady=10)
        
        self.blocked_listbox = tk.Listbox(blocked_frame, bg='#16213e', fg='#ff8888',
                                          font=('Courier', 10), height=6,
                                          selectbackground='#ff4444')
        self.blocked_listbox.pack(side='left', fill='both', expand=True)
        
        btn_frame = tk.Frame(blocked_frame, bg='#1a1a2e')
        btn_frame.pack(side='right', padx=10)
        
        self.unblock_btn = tk.Button(btn_frame, text="🔓 DESBLOQUEAR", command=self.unblock_selected,
                                    bg='#ff8800', fg='white', font=('Arial', 11, 'bold'),
                                    padx=20, pady=10, cursor='hand2', state='disabled')
        self.unblock_btn.pack()
        
        # Bind de seleção
        self.blocked_listbox.bind('<<ListboxSelect>>', self.on_select_blocked)
        
        # Iniciar atualização automática
        self.start_auto_refresh()
        
    def toggle_firewall(self, event=None):
        """Alterna o firewall entre ligado/desligado"""
        def run():
            if self.firewall_status == False:  # Está inativo, vai ativar
                self.animate_switch(True)
                result = subprocess.run("sudo ufw --force enable", shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    self.app.logs_tab.add_log("🔥 Firewall ATIVADO com sucesso", "success")
                    self.after(0, lambda: self.detail_label.config(text="Firewall está protegendo o sistema", fg='#00ff88'))
                else:
                    self.app.logs_tab.add_log("❌ Erro ao ativar firewall", "error")
                    self.after(0, self.refresh_status)
            else:  # Está ativo, vai desativar
                self.animate_switch(False)
                result = subprocess.run("sudo ufw disable", shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    self.app.logs_tab.add_log("⚠️ Firewall DESATIVADO - Sistema vulnerável", "warning")
                    self.after(0, lambda: self.detail_label.config(text="Firewall está DESATIVADO!", fg='#ff4444'))
                else:
                    self.app.logs_tab.add_log("❌ Erro ao desativar firewall", "error")
                    self.after(0, self.refresh_status)
            
            self.after(0, self.refresh_status)
            self.after(0, self.update_rules)
            self.after(0, self.update_blocked_ips)
            
        threading.Thread(target=run, daemon=True).start()
        
    def animate_switch(self, active):
        """Anima o interruptor"""
        if active:
            # Mover para a direita (ativado)
            self.switch_canvas.coords(self.switch_button, 48, 8, 68, 28)
            self.switch_canvas.itemconfig(self.switch_bg, fill='#00ff88')
            self.switch_canvas.itemconfig(self.switch_text, text="ON", fill='#1a1a2e')
        else:
            # Mover para a esquerda (desativado)
            self.switch_canvas.coords(self.switch_button, 8, 8, 28, 28)
            self.switch_canvas.itemconfig(self.switch_bg, fill='#555')
            self.switch_canvas.itemconfig(self.switch_text, text="OFF", fill='white')
            
    def refresh_status(self):
        """Atualiza o status do firewall"""
        try:
            result = subprocess.run("sudo ufw status", shell=True, capture_output=True, text=True)
            
            if "Status: active" in result.stdout:
                self.firewall_status = True
                self.status_label.config(text="🔥 FIREWALL ATIVO", fg='#00ff88')
                self.detail_label.config(text="Firewall está protegendo o sistema", fg='#00ff88')
                self.animate_switch(True)
                self.update_stats()
            else:
                self.firewall_status = False
                self.status_label.config(text="❌ FIREWALL INATIVO", fg='#ff4444')
                self.detail_label.config(text="Firewall está DESATIVADO! Clique no interruptor para ativar", fg='#ff4444')
                self.animate_switch(False)
                
        except Exception as e:
            self.firewall_status = None
            self.status_label.config(text="⚠️ ERRO AO VERIFICAR", fg='#ffaa00')
            self.detail_label.config(text=f"Erro: {str(e)[:50]}", fg='#ffaa00')
            
    def update_stats(self):
        """Atualiza estatísticas do firewall"""
        try:
            # Contar regras
            result = subprocess.run("sudo ufw status numbered | grep -c '\\['", 
                                   shell=True, capture_output=True, text=True)
            rules_count = max(0, int(result.stdout.strip()) - 1) if result.stdout else 0
            self.stats_labels["Regras ativas"].config(text=str(rules_count))
            
            # Contar IPs bloqueados
            if self.app.defense_engine:
                blocked = len(self.app.defense_engine.get_blocked_ips())
                self.stats_labels["IPs bloqueados"].config(text=str(blocked))
                
        except:
            pass
            
    def update_rules(self):
        """Atualiza a lista de regras"""
        try:
            result = subprocess.run("sudo ufw status numbered", shell=True, capture_output=True, text=True)
            self.rules_text.delete('1.0', 'end')
            if result.stdout and "Status:" in result.stdout:
                self.rules_text.insert('1.0', result.stdout)
            else:
                self.rules_text.insert('1.0', "Nenhuma regra configurada ou UFW não está ativo")
        except:
            self.rules_text.delete('1.0', 'end')
            self.rules_text.insert('1.0', "Erro ao carregar regras")
            
    def update_blocked_ips(self):
        """Atualiza lista de IPs bloqueados"""
        self.blocked_listbox.delete(0, 'end')
        if self.app.defense_engine:
            for ip in self.app.defense_engine.get_blocked_ips():
                self.blocked_listbox.insert('end', ip)
        if self.blocked_listbox.size() == 0:
            self.blocked_listbox.insert('end', "Nenhum IP bloqueado")
            
    def on_select_blocked(self, event):
        """Quando um IP é selecionado na lista"""
        selection = self.blocked_listbox.curselection()
        if selection and self.blocked_listbox.get(selection[0]) != "Nenhum IP bloqueado":
            self.unblock_btn.config(state='normal')
        else:
            self.unblock_btn.config(state='disabled')
            
    def unblock_selected(self):
        """Desbloqueia o IP selecionado"""
        selection = self.blocked_listbox.curselection()
        if selection:
            ip = self.blocked_listbox.get(selection[0])
            if ip and ip != "Nenhum IP bloqueado":
                def run():
                    if self.app.defense_engine and self.app.defense_engine.unblock_ip(ip):
                        self.app.logs_tab.add_log(f"🔓 IP {ip} desbloqueado", "success")
                        self.after(0, self.update_blocked_ips)
                        self.after(0, self.update_rules)
                    else:
                        # Tentar desbloquear via UFW diretamente
                        result = subprocess.run(f"sudo ufw delete deny from {ip}", 
                                               shell=True, capture_output=True)
                        if result.returncode == 0:
                            self.app.logs_tab.add_log(f"🔓 IP {ip} desbloqueado via UFW", "success")
                            self.after(0, self.update_blocked_ips)
                            self.after(0, self.update_rules)
                        else:
                            self.app.logs_tab.add_log(f"❌ Falha ao desbloquear {ip}", "error")
                threading.Thread(target=run, daemon=True).start()
                
    def start_auto_refresh(self):
        """Atualiza automaticamente a cada 3 segundos"""
        def refresh_loop():
            while True:
                if self.winfo_exists():
                    self.after(0, self.refresh_status)
                    self.after(0, self.update_rules)
                    self.after(0, self.update_blocked_ips)
                    self.after(0, self.update_stats)
                time.sleep(3)
        threading.Thread(target=refresh_loop, daemon=True).start()
