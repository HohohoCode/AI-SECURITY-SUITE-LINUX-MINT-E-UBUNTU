"""
ANÁLISE COMPORTAMENTAL DE USUÁRIOS
- Perfil de comportamento normal
- Detecção de anomalias em ações
- Prevenção de movimentação lateral
"""

import threading
import time
import subprocess
import re
from collections import deque
from datetime import datetime
from typing import Dict, List

class BehavioralAnalyzer:
    """Analisador comportamental de usuários e processos"""
    
    def __init__(self, callback=None):
        self.callback = callback
        self.is_running = False
        self.user_profiles = {}
        self.process_history = deque(maxlen=1000)
        self.anomaly_threshold = 0.7
        
        # Processos legítimos do sistema (lista expandida)
        self.legitimate_processes = [
            # Sistema
            "/sbin/init", "systemd", "kernel", "kthreadd", "rcu", "migration",
            "ksoftirqd", "kworker", "kdevtmpfs", "netns", "kauditd", "khungtaskd",
            "oom_reaper", "writeback", "kcompactd", "ksmd", "khugepaged", "crypto",
            "kintegrityd", "kblockd", "blkcg_punt", "tpm_dev_wq", "ata_sff",
            "scsi_eh_0", "scsi_tmf_0", "ipv6_addrconf", "strp", "kstrp", "ttm_swap",
            "bioset", "deferwq", "psimon", "kdmflush", "kcryptd_io", "kcryptd",
            "jbd2", "ext4-rsv-conver", "loop0", "loop1", "loop2",
            
            # Serviços do sistema
            "systemd-journal", "systemd-udevd", "systemd-logind", "systemd-timesyncd",
            "systemd-resolved", "systemd-network", "systemd-hostnamed", "systemd-localed",
            "dbus-daemon", "dbus-broker", "NetworkManager", "ModemManager", 
            "accounts-daemon", "avahi-daemon", "bluetoothd", "colord", "cupsd",
            "cups-browsed", "fwupd", "geoclue", "goa-daemon", "gsd-", "udisksd",
            "upowerd", "thermald", "switcheroo-control", "rtkit-daemon", "polkitd",
            "packagekitd", "ntpd", "chronyd", "snapd", "flatpak", "apparmor",
            
            # Interface gráfica
            "gnome-shell", "gnome-terminal-", "nautilus", "nemo", "cinnamon",
            "xfce4-terminal", "mate-terminal", "kwin_x11", "plasmashell", "dolphin",
            "konsole", "budgie-wm", "pantheon-files", "lxqt-session", "openbox",
            "i3", "sway", "awesome", "xmonad", "bspwm", "herbstluftwm",
            
            # Navegadores
            "firefox", "firefox-bin", "chrome", "chromium", "chromium-browser",
            "brave-browser", "opera", "vivaldi", "edge", "epiphany", "webkit",
            
            # Aplicativos comuns
            "spotify", "vlc", "totem", "rhythmbox", "audacious", "clementine",
            "libreoffice", "onlyoffice", "wps", "gimp", "inkscape", "krita",
            "blender", "obs", "simplescreenrecorder", "kazam", "peek",
            
            # Editores e IDEs
            "code", "code-insiders", "cursor", "vscode", "atom", "sublime_text",
            "gedit", "kate", "mousepad", "leafpad", "nano", "vim", "nvim", "emacs",
            "pycharm", "intellij", "webstorm", "phpstorm", "clion", "rider", "goland",
            
            # Terminais e shells
            "bash", "zsh", "fish", "dash", "sh", "tmux", "screen", "byobu",
            
            # Utilitários do sistema
            "gvfsd", "gvfsd-trash", "gvfsd-metadata", "gvfsd-http", "gvfsd-dnssd",
            "gvfsd-smb", "gvfsd-ftp", "gvfsd-network", "gvfsd-mtp", "gvfsd-afc",
            "dconf-service", "evolution-data-server", "goa-daemon", "gsd-xsettings",
            "gsd-keyboard", "gsd-media-keys", "gsd-power", "gsd-print-notifications",
            "gsd-rfkill", "gsd-screensaver-proxy", "gsd-sharing", "gsd-smartcard",
            "gsd-sound", "gsd-wacom", "gsd-housekeeping", "gsd-datetime",
            
            # QtWebEngine (usado por muitos apps)
            "QtWebEngineProcess", "QtWebEngineProce", "qwebengine", "webengine",
            
            # Flatpak/Snap
            "flatpak", "flatpak-session-helper", "snapd", "snap-confine",
            
            # Python (quando não malicioso)
            "python3", "python", "python2", "ipython", "jupyter",
            
            # Node.js (quando não malicioso)
            "node", "npm", "yarn", "pnpm", "bun", "deno",
            
            # Docker/Container
            "docker", "docker-containerd", "dockerd", "containerd", "runc",
            
            # Virtualização
            "qemu", "kvm", "virt-manager", "virtualbox", "vmware", "gnome-boxes"
        ]
        
        # Padrões MALICIOSOS reais (não falsos positivos)
        self.malicious_patterns = [
            # Reverse shells
            r"nc\s+.*-e\s+/bin/sh", r"nc\s+.*-e\s+/bin/bash",
            r"bash\s+-i\s+>&\s+/dev/tcp/", r"python -c 'import socket.*subprocess",
            r"perl -e 'use Socket.*exec", r"ruby -rsocket -e",
            r"php -r '\$sock=fsockopen", r"telnet.*\|.*/bin/sh",
            
            # Download e execução de malware
            r"curl.*\|.*sh", r"wget.*\|.*sh", r"curl.*\|.*bash",
            r"wget.*-O-.*\|.*sh", r"curl.*http.*\|.*python",
            
            # Ferramentas de hacking
            r"nmap -sS", r"nmap -sC", r"nmap -A", r"masscan", r"zmap",
            r"hydra", r"medusa", r"ncrack", r"thc-hydra", r"john", r"hashcat",
            r"sqlmap", r"nikto", r"dirb", r"gobuster", r"wfuzz", r"ffuf",
            r"metasploit", r"msfconsole", r"msfvenom", r"msfrpc",
            r"aircrack-ng", r"reaver", r"bully", r"pixiewps",
            r"ettercap", r"arpspoof", r"driftnet", r"urlsnarf", r"msgsnarf",
            r"tcpdump -w", r"tshark -w", r"dumpcap",
            
            # Backdoors
            r"\./backdoor", r"\./shell", r"\./payload", r"\./reverse",
            
            # Criptomineração
            r"xmrig", r"cpuminer", r"miner", r"stratum", r"nicehash",
            
            # Exploração
            r"searchsploit", r"exploit", r"shellshock", r"heartbleed"
        ]
        
    def start(self):
        """Inicia a análise comportamental"""
        self.is_running = True
        self._log("📊 Análise Comportamental ativada", "success")
        self.monitor_thread = threading.Thread(target=self._monitor, daemon=True)
        self.monitor_thread.start()
    
    def stop(self):
        self.is_running = False
        self._log("📊 Análise Comportamental desativada", "warning")
    
    def _is_legitimate_process(self, process_line):
        """Verifica se o processo é legítimo do sistema"""
        process_lower = process_line.lower()
        
        # Verificar na lista de processos legítimos
        for legit in self.legitimate_processes:
            if legit.lower() in process_lower:
                return True
        
        # Verificar caminhos comuns de aplicativos legítimos
        legitimate_paths = [
            "/usr/bin/", "/usr/sbin/", "/bin/", "/sbin/", "/usr/lib/",
            "/usr/libexec/", "/snap/", "/var/lib/flatpak/", "/app/lib/",
            "/opt/", "/home/", "/usr/share/"
        ]
        
        # Se o processo está em um caminho legítimo e não tem padrão malicioso
        for path in legitimate_paths:
            if path in process_lower:
                # Verificar se contém padrão malicioso
                for pattern in self.malicious_patterns:
                    if re.search(pattern, process_lower):
                        return False
                return True
        
        return False
    
    def _monitor(self):
        while self.is_running:
            try:
                self._analyze_user_behavior()
                self._analyze_process_behavior()
                self._detect_lateral_movement()
                time.sleep(5)
            except:
                pass
    
    def _analyze_user_behavior(self):
        """Analisa comportamento de usuários logados"""
        try:
            # Obter usuários logados
            result = subprocess.run("who | awk '{print $1}' | sort -u", shell=True, capture_output=True, text=True)
            users = result.stdout.strip().split('\n') if result.stdout else []
            
            for user in users:
                if not user or user == "root":
                    continue
                
                # Obter processos do usuário
                result = subprocess.run(f"ps -u {user} --no-headers | wc -l", shell=True, capture_output=True, text=True)
                process_count = int(result.stdout.strip()) if result.stdout else 0
                
                # Obter conexões de rede do usuário
                result = subprocess.run(f"ss -tun state established 2>/dev/null | grep -c 'estab'", shell=True, capture_output=True, text=True)
                connections = int(result.stdout.strip()) if result.stdout else 0
                
                # Criar perfil se não existir
                if user not in self.user_profiles:
                    self.user_profiles[user] = {
                        "process_history": deque(maxlen=50),
                        "conn_history": deque(maxlen=50),
                        "anomaly_score": 0,
                        "last_seen": time.time()
                    }
                
                profile = self.user_profiles[user]
                profile["process_history"].append(process_count)
                profile["conn_history"].append(connections)
                profile["last_seen"] = time.time()
                
                # Calcular anomalia
                if len(profile["process_history"]) > 10:
                    mean_proc = sum(profile["process_history"]) / len(profile["process_history"])
                    std_proc = (sum((x - mean_proc)**2 for x in profile["process_history"]) / len(profile["process_history"])) ** 0.5
                    
                    if process_count > mean_proc + 3 * std_proc and process_count > 100:
                        profile["anomaly_score"] = min(1.0, profile["anomaly_score"] + 0.2)
                        self._log(f"⚠️ Usuário {user} com número anormal de processos: {process_count} (média: {mean_proc:.0f})", "alert")
        except:
            pass
    
    def _analyze_process_behavior(self):
        """Analisa comportamento de processos suspeitos (apenas reais ameaças)"""
        try:
            # Obter lista de processos
            result = subprocess.run("ps aux", shell=True, capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')[1:]  # Pular cabeçalho
            
            for line in lines:
                if not line:
                    continue
                
                # Verificar se é processo legítimo
                if self._is_legitimate_process(line):
                    continue
                
                # Verificar padrões maliciosos
                line_lower = line.lower()
                for pattern in self.malicious_patterns:
                    if re.search(pattern, line_lower):
                        # Extrair PID e comando
                        parts = line.split()
                        if len(parts) >= 11:
                            pid = parts[1]
                            cmd = ' '.join(parts[10:])
                            self._log(f"🚨 PROCESSO MALICIOSO DETECTADO: PID={pid} CMD={cmd[:100]}", "critical")
                            
                            if self.callback:
                                self.callback({
                                    "type": "suspicious_process",
                                    "pid": pid,
                                    "command": cmd[:200],
                                    "pattern": pattern
                                })
                        break
        except:
            pass
    
    def _detect_lateral_movement(self):
        """Detecta movimentação lateral (pivoting)"""
        try:
            # Verificar conexões SSH para outras máquinas
            result = subprocess.run("ss -tun state established 2>/dev/null | grep ':22 ' | awk '{print $5}'", 
                                   shell=True, capture_output=True, text=True)
            if result.stdout:
                connections = result.stdout.strip().split('\n')
                for conn in connections:
                    if conn and ':' in conn:
                        ip = conn.split(':')[0]
                        # Ignorar IPs locais
                        if not ip.startswith(('10.', '192.168.', '172.', '127.')) and ip != "0.0.0.0":
                            self._log(f"🔄 Conexão SSH externa detectada para {ip}", "alert")
        except:
            pass
    
    def get_stats(self):
        return {
            "total_users": len(self.user_profiles),
            "anomalies_detected": sum(1 for p in self.user_profiles.values() if p["anomaly_score"] > 0.5),
            "active_users": sum(1 for p in self.user_profiles.values() if time.time() - p["last_seen"] < 300)
        }
    
    def _log(self, msg, level="info"):
        if self.callback:
            self.callback({"type": "log", "message": f"[BEHAVIOR] {msg}", "level": level})
        print(f"[BEHAVIOR] {msg}")
