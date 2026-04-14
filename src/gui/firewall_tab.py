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
        tk.Label(title_frame, text="Gerencie o firewall e os IPs bloqueados", 
                bg='#0a0a1a', fg='#888', font=('Arial', 10)).pack()
        
        # Card principal com interruptor
        main_card = tk.Frame(self, bg='#16213e', relief='ridge', bd=2)
        main_card.pack(fill='x', padx=30, pady=20)
        
        status_frame = tk.Frame(main_card, bg='#16213e')
        status_frame.pack(pady=30)
        
        # Interruptor ON/OFF
        self.switch_canvas = tk.Canvas(status_frame, width=100, height=45, bg='#16213e', highlightthickness=0)
        self.switch_canvas.pack()
        self.switch_bg = self.switch_canvas.create_rectangle(5, 5, 95, 40, fill='#555', outline='')
        self.switch_btn = self.switch_canvas.create_oval(8, 8, 37, 37, fill='white', outline='')
        self.switch_text = self.switch_canvas.create_text(70, 23, text="OFF", fill='white', font=('Arial', 11, 'bold'))
        self.switch_canvas.tag_bind(self.switch_bg, '<Button-1>', self.toggle)
        self.switch_canvas.tag_bind(self.switch_btn, '<Button-1>', self.toggle)
        
        self.status_label = tk.Label(main_card, text="", bg='#16213e', font=('Arial', 12))
        self.status_label.pack(pady=10)
        
        # ============ IPs BLOQUEADOS ============
        blocked_frame = tk.LabelFrame(self, text="🚫 IPs BLOQUEADOS PELA IA", 
                                       bg='#16213e', fg='#ff4444', font=('Arial', 12, 'bold'))
        blocked_frame.pack(fill='x', padx=30, pady=10)
        
        # Lista de IPs bloqueados
        self.blocked_listbox = tk.Listbox(blocked_frame, bg='#0a0a1a', fg='#ff8888', 
                                           font=('Courier', 11), height=8)
        self.blocked_listbox.pack(fill='x', padx=10, pady=10)
        
        # Botões apenas: Desbloquear e Limpar Tudo
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
        
        # Bind de seleção na lista
        self.blocked_listbox.bind('<<ListboxSelect>>', self.on_select)
        
        # ============ REGRAS DO FIREWALL ============
        rules_frame = tk.LabelFrame(self, text="📋 REGRAS DO FIREWALL", 
                                     bg='#16213e', fg='#00ff88', font=('Arial', 12, 'bold'))
        rules_frame.pack(fill='both', expand=True, padx=30, pady=10)
        
        self.rules_text = scrolledtext.ScrolledText(rules_frame, bg='#0a0a1a', fg='#00ff88', 
                                                     font=('Courier', 10), height=12)
        self.rules_text.pack(fill='both', expand=True, padx=10, pady=10)
        
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
    
    def on_select(self, event):
        """Quando um IP é selecionado na lista"""
        selection = self.blocked_listbox.curselection()
        if selection and self.blocked_listbox.get(selection[0]) != "Nenhum IP bloqueado":
            self.unblock_btn.config(state='normal')
        else:
            self.unblock_btn.config(state='disabled')
    
    def unblock_selected(self):
        """Desbloqueia o IP selecionado"""
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
                        self.refresh_status()
                    else:
                        self.app.logs_tab.add_log(f"❌ {msg}", "error")
                threading.Thread(target=run, daemon=True).start()
    
    def clear_all_blocked(self):
        """Remove todos os IPs bloqueados"""
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
                self.refresh_status()
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
        self.unblock_btn.config(state='disabled')
    
    def start_auto_refresh(self):
        def refresh_loop():
            while True:
                if self.winfo_exists():
                    self.update_rules()
                    self.update_blocked_ips()
                time.sleep(3)
        threading.Thread(target=refresh_loop, daemon=True).start()
