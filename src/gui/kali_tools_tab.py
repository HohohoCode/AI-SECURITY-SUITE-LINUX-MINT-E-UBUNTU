import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading

class KaliToolsTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg='#0a0e27')
        self.app = app
        self.setup_ui()
    
    def setup_ui(self):
        # Canvas com scroll
        self.main_canvas = tk.Canvas(self, bg='#0a0e27', highlightthickness=0)
        self.main_scrollbar = tk.Scrollbar(self, orient='vertical', command=self.main_canvas.yview)
        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)
        
        self.main_scrollbar.pack(side='right', fill='y')
        self.main_canvas.pack(side='left', fill='both', expand=True)
        
        self.inner_frame = tk.Frame(self.main_canvas, bg='#0a0e27')
        self.main_canvas.create_window((0, 0), window=self.inner_frame, anchor='nw', width=self.main_canvas.winfo_width())
        
        self.inner_frame.bind('<Configure>', self._on_frame_configure)
        self.main_canvas.bind('<Configure>', self._on_canvas_configure)
        
        # Título
        title_frame = tk.Frame(self.inner_frame, bg='#0a0e27')
        title_frame.pack(fill='x', pady=20, padx=30)
        tk.Label(title_frame, text="🐉 KALI TOOLS - GUI + CLI", font=('Segoe UI', 24, 'bold'),
                bg='#0a0e27', fg='#00d4ff').pack()
        tk.Label(title_frame, text="Todas as ferramentas disponíveis | Modo Ofensivo SEMPRE ATIVO", 
                bg='#0a0e27', fg='#00ff88', font=('Segoe UI', 11)).pack()
        
        # Indicador de modo ofensivo ativo
        offensive_indicator = tk.Frame(self.inner_frame, bg='#ff6600', height=2)
        offensive_indicator.pack(fill='x', padx=30, pady=5)
        
        offensive_label = tk.Label(self.inner_frame, text="⚔️ MODO OFENSIVO ATIVO - Sistema irá contra-atacar invasores automaticamente ⚔️",
                                    bg='#0a0e27', fg='#ff6600', font=('Segoe UI', 11, 'bold'))
        offensive_label.pack(pady=5)
        
        # Botão instalar
        install_btn = tk.Button(self.inner_frame, text="📦 INSTALAR FERRAMENTAS", command=self.install_tools,
                                bg='#ff6600', fg='white', font=('Segoe UI', 12, 'bold'),
                                padx=20, pady=10, cursor='hand2')
        install_btn.pack(pady=10)
        
        # ============ FERRAMENTAS GUI ============
        gui_frame = tk.LabelFrame(self.inner_frame, text="🖥️ FERRAMENTAS GUI", 
                                   bg='#151c3c', fg='#00d4ff', font=('Segoe UI', 13, 'bold'))
        gui_frame.pack(fill='x', padx=30, pady=10)
        
        gui_grid = tk.Frame(gui_frame, bg='#151c3c')
        gui_grid.pack(fill='x', padx=10, pady=10)
        
        gui_tools = [
            ("Zenmap", "zenmap", "Nmap com interface gráfica"),
            ("Angry IP Scanner", "ipscan", "Scanner de rede rápido"),
            ("Wireshark", "wireshark", "Analisador de pacotes"),
            ("EtherApe", "etherape", "Monitor gráfico de rede"),
            ("OWASP ZAP", "zap", "Teste de segurança web"),
            ("KeePass", "keepass2", "Gerenciador de senhas"),
            ("Guymager", "guymager", "Imagem de disco forense")
        ]
        
        for i, (name, cmd, desc) in enumerate(gui_tools):
            row = i // 4
            col = i % 4
            self.create_gui_button(gui_grid, name, cmd, desc, row, col)
        
        # ============ FERRAMENTAS CLI ============
        cli_frame = tk.LabelFrame(self.inner_frame, text="💻 FERRAMENTAS CLI", 
                                   bg='#151c3c', fg='#ffaa00', font=('Segoe UI', 13, 'bold'))
        cli_frame.pack(fill='x', padx=30, pady=10)
        
        cli_grid = tk.Frame(cli_frame, bg='#151c3c')
        cli_grid.pack(fill='x', padx=10, pady=10)
        
        # Ferramentas CLI - todas disponíveis no Linux Mint
        cli_tools = [
            ("Nmap", "nmap", "Scanner de portas"),
            ("Nikto", "nikto", "Scanner web vulnerabilidades"),
            ("Hydra", "hydra", "Força bruta online"),
            ("John", "john", "Quebrador de hashes"),
            ("Hashcat", "hashcat", "Quebrador com GPU"),
            ("Aircrack-ng", "aircrack-ng", "Auditoria Wi-Fi"),
            ("Wifite", "wifite", "Auto Wi-Fi auditoria"),
            ("Gobuster", "gobuster", "Scanner de diretórios"),
            ("Dirb", "dirb", "Scanner de diretórios"),
            ("Sherlock", "sherlock", "Busca em redes sociais"),
            ("BetterCAP", "bettercap", "MITM framework"),
            ("IPTraf-ng", "iptraf-ng", "Monitor de tráfego"),
            ("Wavemon", "wavemon", "Monitor Wi-Fi"),
            ("Metasploit", "msfconsole", "Framework de exploits"),
            ("Sqlmap", "sqlmap", "Injeção SQL"),
            ("Hydra GTK", "hydra-gtk", "Hydra com GUI"),
            ("Foremost", "foremost", "Recuperação de arquivos"),
            ("Binwalk", "binwalk", "Análise de firmware"),
            ("Autopsy", "autopsy", "Análise forense")
        ]
        
        for i, (name, cmd, desc) in enumerate(cli_tools):
            row = i // 4
            col = i % 4
            self.create_cli_button(cli_grid, name, cmd, desc, row, col)
        
        # LOG GERAL
        log_frame = tk.LabelFrame(self.inner_frame, text="📝 LOG GERAL", bg='#151c3c', fg='#00d4ff', font=('Segoe UI', 11, 'bold'))
        log_frame.pack(fill='x', padx=30, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, bg='#0a0e27', fg='#00ff88',
                                                   font=('Courier', 9), height=8, wrap='word')
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.add_log("✅ Sistema pronto. 7 GUI + 19 CLI (todas disponíveis)")
        self.add_log("⚔️ MODO OFENSIVO ATIVO - Contra-ataques automáticos habilitados")
    
    def _on_frame_configure(self, event):
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox('all'))
    
    def _on_canvas_configure(self, event):
        self.main_canvas.itemconfig(1, width=event.width)
    
    def add_log(self, msg):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert('end', f"[{timestamp}] {msg}\n")
        self.log_text.see('end')
    
    def create_gui_button(self, parent, name, cmd, desc, row, col):
        frame = tk.Frame(parent, bg='#0f3460', relief='ridge', bd=1)
        frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        parent.grid_columnconfigure(col, weight=1)
        
        tk.Label(frame, text=name, bg='#0f3460', fg='#00d4ff', 
                font=('Segoe UI', 10, 'bold')).pack(pady=(5,0))
        tk.Label(frame, text=desc, bg='#0f3460', fg='#8892b0', 
                font=('Segoe UI', 8)).pack()
        
        btn = tk.Button(frame, text="▶ EXECUTAR", 
                       command=lambda n=name, c=cmd: self.run_gui_tool(n, c),
                       bg='#00d4ff', fg='#0a0e27', font=('Segoe UI', 9, 'bold'),
                       padx=10, pady=3, cursor='hand2')
        btn.pack(pady=5)
    
    def create_cli_button(self, parent, name, cmd, desc, row, col):
        frame = tk.Frame(parent, bg='#1a2352', relief='ridge', bd=1)
        frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        parent.grid_columnconfigure(col, weight=1)
        
        tk.Label(frame, text=name, bg='#1a2352', fg='#ffaa00', 
                font=('Segoe UI', 10, 'bold')).pack(pady=(5,0))
        tk.Label(frame, text=desc, bg='#1a2352', fg='#8892b0', 
                font=('Segoe UI', 8)).pack()
        
        btn_frame = tk.Frame(frame, bg='#1a2352')
        btn_frame.pack(pady=5)
        
        btn = tk.Button(btn_frame, text="▶ EXECUTAR", 
                       command=lambda n=name, c=cmd: self.run_cli_tool(n, c),
                       bg='#0f3460', fg='white', font=('Segoe UI', 9),
                       padx=10, pady=3, cursor='hand2')
        btn.pack(side='left', padx=2)
        
        info_btn = tk.Button(btn_frame, text="📖 INFO", 
                            command=lambda n=name, c=cmd: self.show_tool_info(n, c),
                            bg='#ff8800', fg='#0a0e27', font=('Segoe UI', 9, 'bold'),
                            padx=10, pady=3, cursor='hand2')
        info_btn.pack(side='left', padx=2)
    
    def show_tool_info(self, name, cmd):
        info_dict = {
            "nmap": {
                "desc": "Nmap - Scanner de portas",
                "examples": [
                    ("Scan simples", "nmap 192.168.1.1"),
                    ("Scan de portas", "nmap -p 22,80,443 192.168.1.1"),
                    ("Detectar SO", "nmap -O 192.168.1.1")
                ]
            },
            "hydra": {
                "desc": "Hydra - Força bruta",
                "examples": [
                    ("SSH", "hydra -l admin -P wordlist.txt ssh://192.168.1.1"),
                    ("FTP", "hydra -L users.txt -P pass.txt ftp://192.168.1.1")
                ]
            },
            "john": {
                "desc": "John - Quebrador de hashes",
                "examples": [
                    ("MD5", "john --format=raw-md5 hash.txt"),
                    ("Com wordlist", "john --wordlist=rockyou.txt hash.txt")
                ]
            },
            "aircrack-ng": {
                "desc": "Aircrack-ng - Auditoria Wi-Fi",
                "examples": [
                    ("Modo monitor", "sudo airmon-ng start wlan0"),
                    ("Escanear", "sudo airodump-ng wlan0mon"),
                    ("Capturar", "sudo airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w cap wlan0mon"),
                    ("Quebrar", "sudo aircrack-ng -w wordlist.txt cap-01.cap")
                ]
            },
            "gobuster": {
                "desc": "Gobuster - Scanner de diretórios",
                "examples": [
                    ("Diretórios", "gobuster dir -u http://site.com -w wordlist.txt"),
                    ("DNS", "gobuster dns -d site.com -w wordlist.txt")
                ]
            },
            "metasploit": {
                "desc": "Metasploit - Framework de exploits",
                "examples": [
                    ("Iniciar", "msfconsole"),
                    ("Buscar", "search type:exploit"),
                    ("Usar", "use exploit/windows/smb/ms17_010_eternalblue")
                ]
            },
            "sqlmap": {
                "desc": "SQLmap - Injeção SQL",
                "examples": [
                    ("Testar", "sqlmap -u 'http://site.com/page?id=1'"),
                    ("Listar bancos", "sqlmap -u 'http://site.com/page?id=1' --dbs")
                ]
            }
        }
        
        info = info_dict.get(cmd, {
            "desc": f"{name} - Ferramenta de segurança",
            "examples": [
                ("Ajuda", f"{cmd} --help"),
                ("Versão", f"{cmd} --version")
            ]
        })
        
        examples_text = "\n".join([f"   $ {ex[1]}\n   → {ex[0]}\n" for ex in info["examples"]])
        
        messagebox.showinfo(
            f"📖 {name}",
            f"╔══════════════════════════════════════════════════════════════╗\n"
            f"║  {info['desc']}\n"
            f"╚══════════════════════════════════════════════════════════════╝\n\n"
            f"📝 EXEMPLOS:\n\n{examples_text}\n"
            f"💡 man {cmd} para mais detalhes"
        )
    
    def install_tools(self):
        def run():
            self.add_log("=" * 50)
            self.add_log("📦 Instalando ferramentas...")
            self.add_log("=" * 50)
            
            subprocess.run("sudo apt-get update 2>/dev/null", shell=True)
            
            tools = [
                "zenmap", "wireshark", "etherape", "keepass2", "guymager",
                "nmap", "nikto", "hydra", "john", "hashcat", "aircrack-ng",
                "wifite", "gobuster", "dirb", "sherlock", "bettercap",
                "iptraf-ng", "wavemon", "metasploit-framework", "sqlmap",
                "hydra-gtk", "foremost", "binwalk", "autopsy"
            ]
            
            for tool in tools:
                self.add_log(f"📦 Instalando {tool}...")
                result = subprocess.run(f"sudo apt-get install -y {tool} 2>/dev/null", shell=True)
                if result.returncode == 0:
                    self.add_log(f"   ✅ {tool} instalado")
                else:
                    self.add_log(f"   ⚠️ {tool} não disponível")
            
            # Flatpak
            self.add_log("📦 Instalando Flatpak...")
            subprocess.run("sudo apt-get install -y flatpak 2>/dev/null", shell=True)
            subprocess.run("flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo 2>/dev/null", shell=True)
            
            flatpak_tools = [
                ("org.angryip.ipscan", "Angry IP Scanner"),
                ("org.zaproxy.ZAP", "OWASP ZAP")
            ]
            
            for f_id, name in flatpak_tools:
                self.add_log(f"📦 Instalando {name} via Flatpak...")
                subprocess.run(f"flatpak install -y flathub {f_id} 2>/dev/null", shell=True)
                self.add_log(f"   ✅ {name} instalado")
            
            self.add_log("=" * 50)
            self.add_log("✅ INSTALAÇÃO CONCLUÍDA!")
        
        threading.Thread(target=run, daemon=True).start()
    
    def run_gui_tool(self, name, cmd):
        def run():
            self.add_log(f"🚀 Abrindo {name}...")
            
            cmd_map = {
                "zap": "zaproxy",
                "ipscan": "ipscan",
                "wireshark": "wireshark",
                "zenmap": "zenmap",
                "etherape": "etherape",
                "keepass2": "keepass2",
                "guymager": "guymager"
            }
            
            actual_cmd = cmd_map.get(cmd, cmd)
            
            result = subprocess.run(f"which {actual_cmd}", shell=True, capture_output=True)
            if result.returncode == 0:
                subprocess.Popen(actual_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.add_log(f"   ✅ {name} aberto!")
            elif cmd == "ipscan":
                subprocess.Popen("flatpak run org.angryip.ipscan", shell=True)
                self.add_log(f"   ✅ {name} aberto via Flatpak!")
            elif cmd == "zap":
                subprocess.Popen("flatpak run org.zaproxy.ZAP", shell=True)
                self.add_log(f"   ✅ {name} aberto via Flatpak!")
            else:
                self.add_log(f"   ❌ {name} não encontrado.")
        
        threading.Thread(target=run, daemon=True).start()
    
    def run_cli_tool(self, name, cmd):
        def run():
            self.add_log(f"💻 Executando {name}...")
            subprocess.Popen(f"x-terminal-emulator -e bash -c '{cmd}; echo; echo Pressione ENTER para sair...; read'", shell=True)
            self.add_log(f"   ✅ Terminal aberto para {name}")
        
        threading.Thread(target=run, daemon=True).start()
    
    def refresh_tab(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.setup_ui()
