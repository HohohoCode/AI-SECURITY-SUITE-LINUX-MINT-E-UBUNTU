import tkinter as tk
from tkinter import ttk, messagebox
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
        # Título
        title_frame = tk.Frame(self, bg='#0a0a1a')
        title_frame.pack(fill='x', pady=20, padx=30)
        tk.Label(title_frame, text="🚫 IPs BLOQUEADOS", font=('Arial', 24, 'bold'),
                bg='#0a0a1a', fg='#ff4444').pack()
        tk.Label(title_frame, text="Lista de IPs bloqueados automaticamente pela IA", 
                bg='#0a0a1a', fg='#888', font=('Arial', 10)).pack()
        
        # Lista de IPs bloqueados
        list_frame = tk.Frame(self, bg='#16213e', relief='ridge', bd=2)
        list_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Container para a lista
        list_container = tk.Frame(list_frame, bg='#16213e')
        list_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(list_container)
        scrollbar.pack(side='right', fill='y')
        
        # Listbox
        self.blocked_listbox = tk.Listbox(list_container, bg='#0a0a1a', fg='#ff8888', 
                                           font=('Courier', 12), height=15,
                                           yscrollcommand=scrollbar.set)
        self.blocked_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.blocked_listbox.yview)
        
        # Botões
        btn_frame = tk.Frame(list_frame, bg='#16213e')
        btn_frame.pack(pady=15)
        
        self.unblock_btn = tk.Button(btn_frame, text="🔓 DESBLOQUEAR SELECIONADO", 
                                      command=self.unblock_selected,
                                      bg='#ff8800', fg='white', font=('Arial', 11, 'bold'),
                                      padx=25, pady=10, cursor='hand2', state='disabled')
        self.unblock_btn.pack(side='left', padx=10)
        
        self.clear_all_btn = tk.Button(btn_frame, text="🗑️ LIMPAR TODOS OS IPs", 
                                        command=self.clear_all_blocked,
                                        bg='#ff4444', fg='white', font=('Arial', 11, 'bold'),
                                        padx=25, pady=10, cursor='hand2')
        self.clear_all_btn.pack(side='left', padx=10)
        
        self.blocked_listbox.bind('<<ListboxSelect>>', self.on_select)
        
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
        self.update_blocked_ips()
    
    def update_blocked_ips(self):
        self.blocked_listbox.delete(0, 'end')
        ips = FirewallUtils.get_blocked_ips()
        if ips:
            for ip in ips:
                self.blocked_listbox.insert('end', ip)
            self.blocked_listbox.insert('end', f"\n--- Total: {len(ips)} IPs bloqueados ---")
        else:
            self.blocked_listbox.insert('end', "Nenhum IP bloqueado")
            self.blocked_listbox.insert('end', "\n--- O sistema está protegido ---")
        self.unblock_btn.config(state='disabled')
    
    def start_auto_refresh(self):
        """Atualização automática a cada 5 segundos"""
        def refresh():
            self.refresh_status()
            self.after(5000, refresh)
        self.after(1000, refresh)
