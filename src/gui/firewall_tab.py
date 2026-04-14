import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
from src.utils.firewall_utils import FirewallUtils

class FirewallTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='#0a0a1a')
        self.app = app
        self.firewall_active = False
        self.setup_ui()
        self.refresh_status()
        self.start_auto_refresh()
        
    def setup_ui(self):
        # Título
        title_frame = tk.Frame(self, bg='#0a0a1a')
        title_frame.pack(fill='x', pady=20, padx=30)
        tk.Label(title_frame, text="🔥 FIREWALL MANAGER", font=('Arial', 24, 'bold'),
                bg='#0a0a1a', fg='#ff8800').pack()
        tk.Label(title_frame, text="Gerencie o firewall e as regras de bloqueio", 
                bg='#0a0a1a', fg='#888', font=('Arial', 10)).pack()
        
        # Card principal
        main_card = tk.Frame(self, bg='#16213e', relief='ridge', bd=2)
        main_card.pack(fill='x', padx=30, pady=20)
        
        status_frame = tk.Frame(main_card, bg='#16213e')
        status_frame.pack(pady=30)
        
        # Interruptor
        self.switch_canvas = tk.Canvas(status_frame, width=100, height=45, bg='#16213e', highlightthickness=0)
        self.switch_canvas.pack()
        self.switch_bg = self.switch_canvas.create_rectangle(5, 5, 95, 40, fill='#555', outline='')
        self.switch_btn = self.switch_canvas.create_oval(8, 8, 37, 37, fill='white', outline='')
        self.switch_text = self.switch_canvas.create_text(70, 23, text="OFF", fill='white', font=('Arial', 11, 'bold'))
        self.switch_canvas.tag_bind(self.switch_bg, '<Button-1>', self.toggle)
        self.switch_canvas.tag_bind(self.switch_btn, '<Button-1>', self.toggle)
        
        self.status_label = tk.Label(main_card, text="", bg='#16213e', font=('Arial', 12))
        self.status_label.pack(pady=10)
        
        # Botões de ação rápidos
        action_frame = tk.Frame(main_card, bg='#16213e')
        action_frame.pack(pady=10)
        
        tk.Button(action_frame, text="🔄 ATUALIZAR STATUS", command=self.refresh_status,
                 bg='#0f3460', fg='white', font=('Arial', 10), padx=15, pady=5, cursor='hand2').pack(side='left', padx=5)
        
        # Botões de limpeza
        cleanup_frame = tk.LabelFrame(self, text="🧹 LIMPEZA DO FIREWALL", bg='#16213e', fg='#ff4444', font=('Arial', 12, 'bold'))
        cleanup_frame.pack(fill='x', padx=30, pady=10)
        
        btn_cleanup = tk.Frame(cleanup_frame, bg='#16213e')
        btn_cleanup.pack(pady=15)
        
        tk.Button(btn_cleanup, text="🗑️ LIMPAR TODAS AS REGRAS", command=self.clear_all_rules,
                 bg='#ff4444', fg='white', font=('Arial', 10, 'bold'), padx=20, pady=8, cursor='hand2').pack(side='left', padx=10)
        
        tk.Button(btn_cleanup, text="🔄 RESETAR PARA PADRÃO", command=self.reset_firewall,
                 bg='#ff8800', fg='white', font=('Arial', 10, 'bold'), padx=20, pady=8, cursor='hand2').pack(side='left', padx=10)
        
        tk.Button(btn_cleanup, text="🚫 LIMPAR IPs BLOQUEADOS", command=self.clear_blocked_ips,
                 bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'), padx=20, pady=8, cursor='hand2').pack(side='left', padx=10)
        
        # IPs bloqueados
        blocked_frame = tk.LabelFrame(self, text="🚫 IPs BLOQUEADOS PELA IA", bg='#16213e', fg='#ff4444', font=('Arial', 12, 'bold'))
        blocked_frame.pack(fill='x', padx=30, pady=10)
        
        # Frame para lista e botões
        blocked_container = tk.Frame(blocked_frame, bg='#16213e')
        blocked_container.pack(fill='x', padx=10, pady=10)
        
        self.blocked_listbox = tk.Listbox(blocked_container, bg='#0a0a1a', fg='#ff8888', font=('Courier', 11), height=6)
        self.blocked_listbox.pack(side='left', fill='both', expand=True)
        
        blocked_buttons = tk.Frame(blocked_container, bg='#16213e')
        blocked_buttons.pack(side='right', padx=10)
        
        tk.Button(blocked_buttons, text="🔓 DESBLOQUEAR", command=self.unblock_selected,
                 bg='#ff8800', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5, cursor='hand2').pack(pady=5)
        
        tk.Button(blocked_buttons, text="🗑️ LIMPAR TUDO", command=self.clear_all_blocked,
                 bg='#ff4444', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5, cursor='hand2').pack(pady=5)
        
        # Regras do firewall
        rules_frame = tk.LabelFrame(self, text="📋 REGRAS DO FIREWALL", bg='#16213e', fg='#00ff88', font=('Arial', 12, 'bold'))
        rules_frame.pack(fill='both', expand=True, padx=30, pady=10)
        
        self.rules_text = scrolledtext.ScrolledText(rules_frame, bg='#0a0a1a', fg='#00ff88', font=('Courier', 10), height=12)
        self.rules_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Botão para remover regra específica
        remove_frame = tk.Frame(rules_frame, bg='#16213e')
        remove_frame.pack(pady=10)
        
        tk.Label(remove_frame, text="Nº da Regra:", bg='#16213e', fg='white').pack(side='left', padx=5)
        self.rule_num_entry = tk.Entry(remove_frame, width=10, bg='#0a0a1a', fg='white', insertbackground='white')
        self.rule_num_entry.pack(side='left', padx=5)
        
        tk.Button(remove_frame, text="🗑️ REMOVER REGRA", command=self.remove_rule_by_number,
                 bg='#ff4444', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5, cursor='hand2').pack(side='left', padx=10)
        
    def animate(self, active):
        if active:
            self.switch_canvas.coords(self.switch_btn, 58, 8, 87, 37)
            self.switch_canvas.itemconfig(self.switch_bg, fill='#00ff88')
            self.switch_canvas.itemconfig(self.switch_text, text="ON", fill='#0a0a1a')
            self.status_label.config(text="FIREWALL ATIVO", fg='#00ff88')
        else:
            self.switch_canvas.coords(self.switch_btn, 8, 8, 37, 37)
            self.switch_canvas.itemconfig(self.switch_bg, fill='#555')
            self.switch_canvas.itemconfig(self.switch_text, text="OFF", fill='white')
            self.status_label.config(text="FIREWALL INATIVO", fg='#ff4444')
            
    def toggle(self, event=None):
        def run():
            if not self.firewall_active:
                if FirewallUtils.enable():
                    self.firewall_active = True
                    self.animate(True)
                    self.app.logs_tab.add_log("🔥 Firewall ATIVADO", "success")
            else:
                if FirewallUtils.disable():
                    self.firewall_active = False
                    self.animate(False)
                    self.app.logs_tab.add_log("⚠️ Firewall DESATIVADO", "warning")
            self.update_rules()
            self.app.dashboard_tab.update_firewall_status()
        threading.Thread(target=run, daemon=True).start()
    
    def clear_all_rules(self):
        """Remove todas as regras"""
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja remover TODAS as regras do firewall?\n\nIsso pode deixar o sistema vulnerável!"):
            def run():
                success, msg = FirewallUtils.delete_all_rules()
                if success:
                    self.app.logs_tab.add_log(f"🧹 {msg}", "success")
                    self.refresh_status()
                else:
                    self.app.logs_tab.add_log(f"❌ {msg}", "error")
            threading.Thread(target=run, daemon=True).start()
    
    def reset_firewall(self):
        """Reseta o firewall para configuração padrão"""
        if messagebox.askyesno("Confirmar", "Resetar o firewall para configuração padrão?\n\nRegras: deny incoming, allow outgoing"):
            def run():
                success, msg = FirewallUtils.reset_to_default()
                if success:
                    self.app.logs_tab.add_log(f"🔄 {msg}", "success")
                    self.refresh_status()
                else:
                    self.app.logs_tab.add_log(f"❌ {msg}", "error")
            threading.Thread(target=run, daemon=True).start()
    
    def clear_blocked_ips(self):
        """Remove apenas os IPs bloqueados (mantém outras regras)"""
        if messagebox.askyesno("Confirmar", "Remover todos os IPs bloqueados?"):
            def run():
                blocked = FirewallUtils.get_blocked_ips()
                removed = 0
                for ip in blocked:
                    success, _ = FirewallUtils.delete_rule_by_ip(ip)
                    if success:
                        removed += 1
                self.app.logs_tab.add_log(f"🧹 {removed} IPs bloqueados removidos", "success")
                self.refresh_status()
            threading.Thread(target=run, daemon=True).start()
    
    def clear_all_blocked(self):
        """Remove todos os IPs bloqueados da lista"""
        self.clear_blocked_ips()
    
    def remove_rule_by_number(self):
        """Remove uma regra específica pelo número"""
        rule_num = self.rule_num_entry.get().strip()
        if not rule_num:
            messagebox.showwarning("Aviso", "Digite o número da regra")
            return
        
        if messagebox.askyesno("Confirmar", f"Remover a regra número {rule_num}?"):
            def run():
                success, msg = FirewallUtils.delete_rule(rule_num)
                if success:
                    self.app.logs_tab.add_log(f"🗑️ {msg}", "success")
                    self.rule_num_entry.delete(0, 'end')
                    self.refresh_status()
                else:
                    self.app.logs_tab.add_log(f"❌ {msg}", "error")
            threading.Thread(target=run, daemon=True).start()
    
    def refresh_status(self):
        def run():
            self.firewall_active = FirewallUtils.get_status()
            self.animate(self.firewall_active)
            self.update_rules()
            self.update_blocked_ips()
        threading.Thread(target=run, daemon=True).start()
    
    def update_rules(self):
        rules = FirewallUtils.get_rules()
        self.rules_text.delete('1.0', 'end')
        self.rules_text.insert('1.0', rules)
    
    def update_blocked_ips(self):
        self.blocked_listbox.delete(0, 'end')
        ips = FirewallUtils.get_blocked_ips()
        if ips:
            for ip in ips:
                self.blocked_listbox.insert('end', ip)
        else:
            self.blocked_listbox.insert('end', "Nenhum IP bloqueado")
    
    def unblock_selected(self):
        selection = self.blocked_listbox.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um IP para desbloquear")
            return
        ip = self.blocked_listbox.get(selection[0])
        if ip and ip != "Nenhum IP bloqueado":
            def run():
                success, msg = FirewallUtils.delete_rule_by_ip(ip)
                if success:
                    self.app.logs_tab.add_log(f"🔓 IP {ip} desbloqueado", "success")
                    self.refresh_status()
                else:
                    self.app.logs_tab.add_log(f"❌ Falha ao desbloquear {ip}", "error")
            threading.Thread(target=run, daemon=True).start()
    
    def start_auto_refresh(self):
        def refresh_loop():
            while True:
                if self.winfo_exists():
                    self.update_rules()
                    self.update_blocked_ips()
                time.sleep(3)
        threading.Thread(target=refresh_loop, daemon=True).start()
