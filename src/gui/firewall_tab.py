import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from src.utils.firewall_utils import FirewallUtils

class FirewallTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='#0a0a1a')
        self.app = app
        self.setup_ui()
        self.refresh_status()
        self.start_auto_refresh()
        
    def setup_ui(self):
        title_frame = tk.Frame(self, bg='#0a0a1a')
        title_frame.pack(fill='x', pady=20, padx=30)
        tk.Label(title_frame, text="🔥 FIREWALL MANAGER", font=('Arial', 24, 'bold'),
                bg='#0a0a1a', fg='#ff8800').pack()
        tk.Label(title_frame, text="Firewall sempre ativo - Proteção contínua", 
                bg='#0a0a1a', fg='#888', font=('Arial', 10)).pack()
        
        status_card = tk.Frame(self, bg='#16213e', relief='ridge', bd=2)
        status_card.pack(fill='x', padx=30, pady=20)
        
        status_frame = tk.Frame(status_card, bg='#16213e')
        status_frame.pack(pady=30)
        
        self.status_indicator = tk.Canvas(status_frame, width=20, height=20, bg='#16213e', highlightthickness=0)
        self.status_indicator.pack(side='left', padx=(0, 15))
        self.status_circle = self.status_indicator.create_oval(2, 2, 18, 18, fill='#00ff88')
        
        self.status_label = tk.Label(status_frame, text="FIREWALL ATIVO", font=('Arial', 20, 'bold'),
                                     bg='#16213e', fg='#00ff88')
        self.status_label.pack(side='left')
        
        tk.Label(status_card, text="O firewall está em execução e protegendo o sistema", 
                bg='#16213e', fg='#888', font=('Arial', 10)).pack(pady=(0, 20))
        
        blocked_frame = tk.LabelFrame(self, text="🚫 IPs BLOQUEADOS PELA IA", 
                                       bg='#16213e', fg='#ff4444', font=('Arial', 12, 'bold'))
        blocked_frame.pack(fill='x', padx=30, pady=10)
        
        self.blocked_listbox = tk.Listbox(blocked_frame, bg='#0a0a1a', fg='#ff8888', 
                                           font=('Courier', 11), height=8)
        self.blocked_listbox.pack(fill='x', padx=10, pady=10)
        
        btn_frame = tk.Frame(blocked_frame, bg='#16213e')
        btn_frame.pack(pady=10)
        
        self.unblock_btn = tk.Button(btn_frame, text="🔓 DESBLOQUEAR SELECIONADO", 
                                      command=self.unblock_selected,
                                      bg='#ff8800', fg='white', font=('Arial', 10, 'bold'),
                                      padx=20, pady=8, cursor='hand2', state='disabled')
        self.unblock_btn.pack(side='left', padx=10)
        
        self.clear_all_btn = tk.Button(btn_frame, text="🗑️ LIMPAR TODOS OS IPs", 
                                        command=self.clear_all_blocked,
                                        bg='#ff4444', fg='white', font=('Arial', 10, 'bold'),
                                        padx=20, pady=8, cursor='hand2')
        self.clear_all_btn.pack(side='left', padx=10)
        
        self.blocked_listbox.bind('<<ListboxSelect>>', self.on_select)
        
        rules_frame = tk.LabelFrame(self, text="📋 REGRAS DO FIREWALL", 
                                     bg='#16213e', fg='#00ff88', font=('Arial', 12, 'bold'))
        rules_frame.pack(fill='both', expand=True, padx=30, pady=10)
        
        self.rules_text = scrolledtext.ScrolledText(rules_frame, bg='#0a0a1a', fg='#00ff88', 
                                                     font=('Courier', 10), height=12)
        self.rules_text.pack(fill='both', expand=True, padx=10, pady=10)
        
    def on_select(self, event):
        selection = self.blocked_listbox.curselection()
        if selection and self.blocked_listbox.get(selection[0]) != "Nenhum IP bloqueado":
            self.unblock_btn.config(state='normal')
        else:
            self.unblock_btn.config(state='disabled')
    
    def unblock_selected(self):
        selection = self.blocked_listbox.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um IP para desbloquear")
            return
        
        ip = self.blocked_listbox.get(selection[0])
        if ip and ip != "Nenhum IP bloqueado":
            if messagebox.askyesno("Confirmar", f"Desbloquear o IP {ip}?"):
                def run():
                    success, msg = FirewallUtils.delete_rule_by_ip(ip)
                    if success:
                        self.app.logs_tab.add_log(f"🔓 {msg}", "success")
                        self.after(100, self.refresh_status)
                    else:
                        self.app.logs_tab.add_log(f"❌ {msg}", "error")
                threading.Thread(target=run, daemon=True).start()
    
    def clear_all_blocked(self):
        blocked = FirewallUtils.get_blocked_ips()
        if not blocked:
            messagebox.showinfo("Info", "Nenhum IP bloqueado para remover")
            return
        
        if messagebox.askyesno("Confirmar", f"Remover TODOS os {len(blocked)} IPs bloqueados?"):
            def run():
                removed = 0
                for ip in blocked:
                    success, _ = FirewallUtils.delete_rule_by_ip(ip)
                    if success:
                        removed += 1
                self.app.logs_tab.add_log(f"🧹 {removed} IPs bloqueados removidos", "success")
                self.after(100, self.refresh_status)
            threading.Thread(target=run, daemon=True).start()
    
    def refresh_status(self):
        self.update_rules()
        self.update_blocked_ips()
    
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
        self.unblock_btn.config(state='disabled')
    
    def start_auto_refresh(self):
        """Atualização automática usando after (thread principal)"""
        def refresh():
            self.refresh_status()
            self.after(5000, refresh)  # Atualiza a cada 5 segundos
        self.after(1000, refresh)
