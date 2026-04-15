import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import time
import re

class ConnectionsTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='#0a0e27')
        self.app = app
        self.setup_ui()
        self.start_refresh()
    
    def setup_ui(self):
        # Título
        title_frame = tk.Frame(self, bg='#0a0e27')
        title_frame.pack(fill='x', pady=20, padx=30)
        tk.Label(title_frame, text="🔗 CONEXÕES DE REDE", font=('Segoe UI', 24, 'bold'),
                bg='#0a0e27', fg='#00d4ff').pack()
        tk.Label(title_frame, text="Gerencie conexões ativas do sistema", 
                bg='#0a0e27', fg='#8892b0', font=('Segoe UI', 11)).pack()
        
        # Frame para tabela
        table_frame = tk.Frame(self, bg='#0a0e27')
        table_frame.pack(fill='both', expand=True, padx=30, pady=10)
        
        # Scrollbars
        scroll_y = ttk.Scrollbar(table_frame)
        scroll_y.pack(side='right', fill='y')
        
        scroll_x = ttk.Scrollbar(table_frame, orient='horizontal')
        scroll_x.pack(side='bottom', fill='x')
        
        # Treeview para conexões
        self.tree = ttk.Treeview(table_frame, columns=("proto", "local", "remote", "state", "pid", "program"), 
                                  show="headings", height=20,
                                  yscrollcommand=scroll_y.set,
                                  xscrollcommand=scroll_x.set)
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        
        # Configurar cabeçalhos
        self.tree.heading("proto", text="Protocolo")
        self.tree.heading("local", text="Endereço Local")
        self.tree.heading("remote", text="Endereço Remoto")
        self.tree.heading("state", text="Estado")
        self.tree.heading("pid", text="PID")
        self.tree.heading("program", text="Programa")
        
        # Configurar larguras
        self.tree.column("proto", width=80, minwidth=80)
        self.tree.column("local", width=250, minwidth=200)
        self.tree.column("remote", width=250, minwidth=200)
        self.tree.column("state", width=100, minwidth=100)
        self.tree.column("pid", width=80, minwidth=80)
        self.tree.column("program", width=200, minwidth=150)
        
        self.tree.pack(fill='both', expand=True)
        
        # Botões de ação
        btn_frame = tk.Frame(self, bg='#0a0e27')
        btn_frame.pack(pady=10)
        
        self.kill_btn = tk.Button(btn_frame, text="🔪 ENCERRAR CONEXÃO", command=self.kill_connection,
                                  bg='#ff4444', fg='white', font=('Segoe UI', 10, 'bold'),
                                  padx=20, pady=8, cursor='hand2', state='disabled')
        self.kill_btn.pack(side='left', padx=10)
        
        self.refresh_btn = tk.Button(btn_frame, text="🔄 ATUALIZAR", command=self.refresh_connections,
                                     bg='#0f3460', fg='white', font=('Segoe UI', 10, 'bold'),
                                     padx=20, pady=8, cursor='hand2')
        self.refresh_btn.pack(side='left', padx=10)
        
        self.kill_process_btn = tk.Button(btn_frame, text="🗑️ ENCERRAR PROCESSO", command=self.kill_process,
                                          bg='#ff8800', fg='white', font=('Segoe UI', 10, 'bold'),
                                          padx=20, pady=8, cursor='hand2', state='disabled')
        self.kill_process_btn.pack(side='left', padx=10)
        
        # Informações adicionais
        info_frame = tk.Frame(self, bg='#151c3c', relief='flat', bd=1)
        info_frame.pack(fill='x', padx=30, pady=10)
        
        tk.Label(info_frame, text="📊 INFORMAÇÕES", font=('Segoe UI', 10, 'bold'),
                bg='#151c3c', fg='#00d4ff').pack(side='left', padx=15, pady=8)
        
        self.conn_count_label = tk.Label(info_frame, text="Conexões: 0", bg='#151c3c', fg='#00ff88', font=('Segoe UI', 9))
        self.conn_count_label.pack(side='left', padx=15)
        
        self.listen_count_label = tk.Label(info_frame, text="Escutando: 0", bg='#151c3c', fg='#ffaa00', font=('Segoe UI', 9))
        self.listen_count_label.pack(side='left', padx=15)
        
        # Bind de seleção
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # Atualizar conexões inicialmente
        self.refresh_connections()
    
    def refresh_connections(self):
        """Atualiza a lista de conexões"""
        def run():
            self.tree.delete(*self.tree.get_children())
            
            established = 0
            listening = 0
            
            try:
                # Usar ss para obter conexões detalhadas
                result = subprocess.run("ss -tunap 2>/dev/null", shell=True, capture_output=True, text=True, timeout=5)
                lines = result.stdout.strip().split('\n')[1:]  # Pular cabeçalho
                
                for line in lines:
                    if not line.strip():
                        continue
                    
                    parts = line.split()
                    if len(parts) >= 6:
                        proto = parts[0]
                        recv_q = parts[1]
                        send_q = parts[2]
                        local = parts[3]
                        remote = parts[4]
                        state = parts[5]
                        
                        # Extrair PID e programa
                        pid_prog = ""
                        pid = ""
                        program = ""
                        if len(parts) >= 7:
                            pid_prog = ' '.join(parts[6:])
                            # Extrair PID
                            pid_match = re.search(r'pid=(\d+)', pid_prog)
                            if pid_match:
                                pid = pid_match.group(1)
                            # Extrair programa
                            prog_match = re.search(r'/"(.+?)"', pid_prog)
                            if prog_match:
                                program = prog_match.group(1)
                            else:
                                program = pid_prog.split(',')[-1] if ',' in pid_prog else pid_prog
                        
                        # Contar conexões estabelecidas
                        if state == "ESTAB":
                            established += 1
                        
                        # Contar portas escutando
                        if "LISTEN" in state:
                            listening += 1
                        
                        # Determinar cor baseada no estado
                        tag = ""
                        if state == "ESTAB":
                            tag = "established"
                        elif "LISTEN" in state:
                            tag = "listening"
                        elif "SYN" in state:
                            tag = "warning"
                        
                        self.tree.insert('', 'end', values=(proto, local, remote, state, pid, program[:50]), tags=(tag,))
                
                # Configurar tags de cor
                self.tree.tag_configure("established", foreground="#00ff88")
                self.tree.tag_configure("listening", foreground="#00d4ff")
                self.tree.tag_configure("warning", foreground="#ffaa00")
                
                # Atualizar contadores
                self.conn_count_label.config(text=f"Conexões: {established}")
                self.listen_count_label.config(text=f"Escutando: {listening}")
                
            except Exception as e:
                self.tree.insert('', 'end', values=("Erro", "", "", f"Erro ao listar conexões: {e}", "", ""))
        
        threading.Thread(target=run, daemon=True).start()
    
    def on_select(self, event):
        """Quando uma conexão é selecionada"""
        selection = self.tree.selection()
        if selection:
            self.kill_btn.config(state='normal')
            self.kill_process_btn.config(state='normal')
        else:
            self.kill_btn.config(state='disabled')
            self.kill_process_btn.config(state='disabled')
    
    def kill_connection(self):
        """Encerra a conexão selecionada usando tcpkill"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma conexão para encerrar")
            return
        
        values = self.tree.item(selection[0])['values']
        if len(values) < 5:
            return
        
        proto = values[0].lower()
        local = values[1]
        remote = values[2]
        
        # Extrair IP e porta
        local_parts = local.split(':')
        remote_parts = remote.split(':')
        
        if len(local_parts) < 2 or len(remote_parts) < 2:
            messagebox.showerror("Erro", "Não foi possível extrair IP/porta")
            return
        
        local_ip = local_parts[0]
        local_port = local_parts[1]
        remote_ip = remote_parts[0]
        remote_port = remote_parts[1]
        
        if messagebox.askyesno("Confirmar", f"Encerrar conexão?\n\n"
                               f"Protocolo: {proto.upper()}\n"
                               f"Local: {local}\n"
                               f"Remoto: {remote}\n\n"
                               f"Esta ação irá resetar a conexão."):
            
            def run():
                try:
                    # Usar tcpkill para encerrar a conexão
                    cmd = f"sudo tcpkill -9 host {remote_ip} and port {remote_port} 2>/dev/null"
                    subprocess.run(cmd, shell=True, timeout=5)
                    self.app.logs_tab.add_log(f"🔪 Conexão encerrada: {remote_ip}:{remote_port}", "success")
                    time.sleep(1)
                    self.refresh_connections()
                except Exception as e:
                    self.app.logs_tab.add_log(f"❌ Erro ao encerrar conexão: {e}", "error")
            
            threading.Thread(target=run, daemon=True).start()
    
    def kill_process(self):
        """Encerra o processo associado à conexão"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma conexão para encerrar o processo")
            return
        
        values = self.tree.item(selection[0])['values']
        if len(values) < 6:
            return
        
        pid = values[4]
        program = values[5]
        
        if not pid or pid == "":
            messagebox.showerror("Erro", "Não foi possível identificar o PID do processo")
            return
        
        if messagebox.askyesno("Confirmar", f"Encerrar processo?\n\n"
                               f"PID: {pid}\n"
                               f"Programa: {program}\n\n"
                               f"Esta ação irá finalizar o processo."):
            
            def run():
                try:
                    subprocess.run(f"sudo kill -9 {pid}", shell=True, timeout=5)
                    self.app.logs_tab.add_log(f"🗑️ Processo {pid} ({program}) encerrado", "success")
                    time.sleep(1)
                    self.refresh_connections()
                except Exception as e:
                    self.app.logs_tab.add_log(f"❌ Erro ao encerrar processo: {e}", "error")
            
            threading.Thread(target=run, daemon=True).start()
    
    def start_refresh(self):
        """Atualização automática a cada 5 segundos"""
        def refresh():
            self.refresh_connections()
            self.after(5000, refresh)
        self.after(2000, refresh)
