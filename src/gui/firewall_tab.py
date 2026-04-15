import tkinter as tk
from tkinter import messagebox
import threading
import re
from src.utils.firewall_utils import FirewallUtils

class FirewallTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='#0a0a1a')
        self.app = app
        self.setup_ui()
        self.start_auto_refresh()
    
    def setup_ui(self):
        tk.Label(self, text="🚫 IPs BLOQUEADOS", font=('Arial', 24, 'bold'),
                bg='#0a0a1a', fg='#ff4444').pack(pady=20)
        
        frame = tk.Frame(self, bg='#16213e', relief='ridge', bd=2)
        frame.pack(fill='both', expand=True, padx=30, pady=10)
        
        self.listbox = tk.Listbox(frame, bg='#0a0a1a', fg='#ff8888', font=('Courier', 11), height=12)
        self.listbox.pack(fill='both', expand=True, padx=10, pady=10)
        
        btn_frame = tk.Frame(frame, bg='#16213e')
        btn_frame.pack(pady=10)
        
        self.unblock_btn = tk.Button(btn_frame, text="🔓 DESBLOQUEAR", command=self.unblock_selected,
                                     bg='#ff8800', fg='white', font=('Arial', 10, 'bold'),
                                     padx=20, pady=8, cursor='hand2', state='disabled')
        self.unblock_btn.pack(side='left', padx=10)
        
        self.clear_btn = tk.Button(btn_frame, text="🗑️ LIMPAR TUDO", command=self.clear_all,
                                   bg='#ff4444', fg='white', font=('Arial', 10, 'bold'),
                                   padx=20, pady=8, cursor='hand2')
        self.clear_btn.pack(side='left', padx=10)
        
        self.reset_btn = tk.Button(btn_frame, text="🔄 RESETAR", command=self.reset_firewall,
                                   bg='#ff6600', fg='white', font=('Arial', 10, 'bold'),
                                   padx=20, pady=8, cursor='hand2')
        self.reset_btn.pack(side='left', padx=10)
        
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        self.update_list()
    
    def on_select(self, event):
        selection = self.listbox.curselection()
        if selection and self.listbox.get(selection[0]) != "Nenhum IP bloqueado":
            self.unblock_btn.config(state='normal')
        else:
            self.unblock_btn.config(state='disabled')
    
    def unblock_selected(self):
        selection = self.listbox.curselection()
        if not selection:
            return
        ip = self.listbox.get(selection[0])
        if ip and ip != "Nenhum IP bloqueado":
            if messagebox.askyesno("Confirmar", f"Desbloquear {ip}?"):
                FirewallUtils.unblock_ip(ip)
                if self.app.defense_engine:
                    self.app.defense_engine.unblock_ip(ip)
                self.update_list()
                self.app.logs_tab.add_log(f"🔓 IP {ip} desbloqueado")
    
    def clear_all(self):
        ips = []
        for i in range(self.listbox.size()):
            item = self.listbox.get(i)
            ip_match = re.search(r'\d+\.\d+\.\d+\.\d+', item)
            if ip_match:
                ips.append(ip_match.group())
        if not ips:
            return
        if messagebox.askyesno("Confirmar", f"Remover {len(ips)} IPs?"):
            for ip in ips:
                FirewallUtils.unblock_ip(ip)
                if self.app.defense_engine:
                    self.app.defense_engine.unblock_ip(ip)
            self.update_list()
            self.app.logs_tab.add_log(f"🧹 {len(ips)} IPs removidos")
    
    def reset_firewall(self):
        if messagebox.askyesno("Confirmar", "Resetar firewall para padrão?"):
            FirewallUtils.reset()
            if self.app.defense_engine:
                self.app.defense_engine.reset_firewall()
            self.update_list()
            self.app.logs_tab.add_log("🔄 Firewall resetado")
    
    def update_list(self):
        self.listbox.delete(0, 'end')
        ips = FirewallUtils.get_blocked_ips()
        if self.app.defense_engine:
            for ip in self.app.defense_engine.get_blocked_ips():
                if ip not in ips:
                    ips.append(ip)
        if ips:
            for ip in ips:
                self.listbox.insert('end', ip)
        else:
            self.listbox.insert('end', "Nenhum IP bloqueado")
        self.unblock_btn.config(state='disabled')
    
    def start_auto_refresh(self):
        def refresh():
            self.update_list()
            self.after(5000, refresh)
        self.after(2000, refresh)
