import tkinter as tk
from tkinter import ttk, messagebox
import threading
import subprocess
import re
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
                                           yscrollcommand=scrollbar.set,
                                           selectbackground='#ff4444',
                                           selectforeground='white')
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
        
        self.refresh_btn = tk.Button(btn_frame, text="🔄 ATUALIZAR", 
                                      command=self.refresh_status,
                                      bg='#0f3460', fg='white', font=('Arial', 11, 'bold'),
                                      padx=25, pady=10, cursor='hand2')
        self.refresh_btn.pack(side='left', padx=10)
        
        self.blocked_listbox.bind('<<ListboxSelect>>', self.on_select)
        
        # Informações adicionais
        info_label = tk.Label(list_frame, text="💡 Clique em um IP para selecionar e depois em DESBLOQUEAR",
                              bg='#16213e', fg='#888', font=('Arial', 9))
        info_label.pack(pady=(0, 10))
        
    def on_select(self, event):
        """Quando um IP é selecionado na lista"""
        selection = self.blocked_listbox.curselection()
        if selection:
            item = self.blocked_listbox.get(selection[0])
            if item and item != "Nenhum IP bloqueado" and not item.startswith("---"):
                self.unblock_btn.config(state='normal')
            else:
                self.unblock_btn.config(state='disabled')
        else:
            self.unblock_btn.config(state='disabled')
    
    def unblock_selected(self):
        """Desbloqueia o IP selecionado"""
        selection = self.blocked_listbox.curselection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um IP para desbloquear")
            return
        
        ip_text = self.blocked_listbox.get(selection[0])
        # Extrair apenas o IP (remover qualquer texto extra)
        ip_match = re.search(r'\d+\.\d+\.\d+\.\d+', ip_text)
        if not ip_match:
            messagebox.showwarning("Aviso", "IP inválido selecionado")
            return
        
        ip = ip_match.group()
        
        if messagebox.askyesno("Confirmar", f"Desbloquear o IP {ip}?"):
            def run():
                try:
                    # Tentar remover via UFW
                    cmd = f"sudo ufw delete deny from {ip}"
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0 or "Rule not found" in result.stdout or "Could not delete" in result.stdout:
                        # Tentar também iptables
                        subprocess.run(f"sudo iptables -D INPUT -s {ip} -j DROP 2>/dev/null", shell=True)
                        self.app.logs_tab.add_log(f"🔓 IP {ip} desbloqueado com sucesso", "success")
                        self.refresh_status()
                    else:
                        self.app.logs_tab.add_log(f"❌ Falha ao desbloquear IP {ip}", "error")
                except Exception as e:
                    self.app.logs_tab.add_log(f"❌ Erro ao desbloquear: {e}", "error")
            threading.Thread(target=run, daemon=True).start()
    
    def clear_all_blocked(self):
        """Remove todos os IPs bloqueados"""
        # Obter todos os IPs da lista
        ips = []
        for i in range(self.blocked_listbox.size()):
            item = self.blocked_listbox.get(i)
            ip_match = re.search(r'\d+\.\d+\.\d+\.\d+', item)
            if ip_match:
                ips.append(ip_match.group())
        
        if not ips:
            messagebox.showinfo("Info", "Nenhum IP bloqueado para remover")
            return
        
        if messagebox.askyesno("Confirmar", f"Remover TODOS os {len(ips)} IPs bloqueados?\n\nIsso pode levar alguns segundos..."):
            def run():
                removed = 0
                for ip in ips:
                    try:
                        cmd = f"sudo ufw delete deny from {ip}"
                        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
                        if result.returncode == 0:
                            removed += 1
                        # Tentar iptables também
                        subprocess.run(f"sudo iptables -D INPUT -s {ip} -j DROP 2>/dev/null", shell=True)
                    except:
                        pass
                
                self.app.logs_tab.add_log(f"🧹 {removed} IPs bloqueados removidos", "success")
                self.refresh_status()
            threading.Thread(target=run, daemon=True).start()
    
    def refresh_status(self):
        """Atualiza a lista de IPs bloqueados"""
        def run():
            self.update_blocked_ips()
        threading.Thread(target=run, daemon=True).start()
    
    def update_blocked_ips(self):
        """Atualiza a lista de IPs bloqueados buscando do UFW"""
        self.blocked_listbox.delete(0, 'end')
        
        ips = []
        
        # Buscar IPs bloqueados no UFW
        try:
            result = subprocess.run("sudo ufw status | grep DENY", shell=True, capture_output=True, text=True, timeout=5)
            lines = result.stdout.strip().split('\n')
            for line in lines:
                ip_match = re.search(r'\d+\.\d+\.\d+\.\d+', line)
                if ip_match:
                    ip = ip_match.group()
                    if ip not in ips:
                        ips.append(ip)
        except:
            pass
        
        # Buscar IPs bloqueados no iptables
        try:
            result = subprocess.run("sudo iptables -L INPUT -n | grep DROP", shell=True, capture_output=True, text=True, timeout=5)
            lines = result.stdout.strip().split('\n')
            for line in lines:
                ip_match = re.search(r'\d+\.\d+\.\d+\.\d+', line)
                if ip_match:
                    ip = ip_match.group()
                    if ip not in ips:
                        ips.append(ip)
        except:
            pass
        
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
            self.update_blocked_ips()
            self.after(5000, refresh)
        self.after(1000, refresh)
