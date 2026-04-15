"""
RESPOSTA PROATIVA
- Isolamento automático de máquinas comprometidas
- Rate limiting dinâmico
- Reset de conexões suspeitas
"""

import subprocess
import threading
import time
import re
from collections import defaultdict
from datetime import datetime

class ProactiveDefense:
    """Sistema de resposta proativa"""
    
    def __init__(self, callback=None):
        self.callback = callback
        self.is_running = False
        self.rate_limits = defaultdict(lambda: {"count": 0, "reset_time": 0})
        self.isolated_ips = set()
        self.connection_blacklist = set()
        
    def start(self):
        self.is_running = True
        self._log("🛡️ Defesa Proativa ativada", "success")
        self.monitor_thread = threading.Thread(target=self._monitor, daemon=True)
        self.monitor_thread.start()
        self.cleanup_thread = threading.Thread(target=self._cleanup, daemon=True)
        self.cleanup_thread.start()
    
    def stop(self):
        self.is_running = False
    
    def _monitor(self):
        while self.is_running:
            try:
                self._apply_rate_limiting()
                self._check_isolation()
                time.sleep(2)
            except:
                pass
    
    def _apply_rate_limiting(self):
        """Aplica rate limiting para conexões suspeitas"""
        try:
            # Obter conexões por IP
            result = subprocess.run("ss -tun state established 2>/dev/null | awk '{print $5}' | cut -d: -f1 | sort | uniq -c",
                                   shell=True, capture_output=True, text=True)
            
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            count = int(parts[0])
                            ip = parts[1]
                            
                            current_time = time.time()
                            limit = self.rate_limits[ip]
                            
                            if limit["reset_time"] < current_time:
                                limit["count"] = 0
                                limit["reset_time"] = current_time + 60
                            
                            limit["count"] += count
                            
                            # Se ultrapassou limite, aplicar throttling
                            if limit["count"] > 100 and ip not in self.isolated_ips:
                                self._apply_throttling(ip)
        except:
            pass
    
    def _apply_throttling(self, ip):
        """Aplica throttling para IP agressivo"""
        try:
            # Adicionar regra de rate limiting no iptables
            cmd = f"sudo iptables -A INPUT -s {ip} -m limit --limit 10/minute -j ACCEPT"
            subprocess.run(cmd, shell=True, capture_output=True)
            cmd = f"sudo iptables -A INPUT -s {ip} -j DROP"
            subprocess.run(cmd, shell=True, capture_output=True)
            
            self.connection_blacklist.add(ip)
            self._log(f"🚦 Rate limiting aplicado para IP {ip}", "warning")
            
            if self.callback:
                self.callback({
                    "type": "rate_limit_applied",
                    "ip": ip,
                    "limit": "10 conexões/minuto"
                })
        except Exception as e:
            self._log(f"Erro ao aplicar rate limiting: {e}", "error")
    
    def isolate_machine(self, ip):
        """Isola uma máquina comprometida"""
        try:
            # Bloquear todo tráfego da máquina
            subprocess.run(f"sudo iptables -A INPUT -s {ip} -j DROP", shell=True)
            subprocess.run(f"sudo iptables -A OUTPUT -d {ip} -j DROP", shell=True)
            subprocess.run(f"sudo iptables -A FORWARD -s {ip} -j DROP", shell=True)
            
            self.isolated_ips.add(ip)
            self._log(f"🔒 Máquina {ip} ISOLADA (comprometida)", "critical")
            
            if self.callback:
                self.callback({
                    "type": "machine_isolated",
                    "ip": ip,
                    "reason": "Comportamento malicioso detectado"
                })
            return True
        except:
            return False
    
    def reset_connection(self, ip, port):
        """Reseta uma conexão suspeita"""
        try:
            # Usar tcpkill para resetar conexão
            cmd = f"sudo tcpkill -9 host {ip} and port {port} 2>/dev/null &"
            subprocess.run(cmd, shell=True)
            self._log(f"🔄 Conexão resetada: {ip}:{port}", "info")
            return True
        except:
            return False
    
    def _check_isolation(self):
        """Verifica se máquinas isoladas ainda estão ativas"""
        for ip in list(self.isolated_ips):
            try:
                result = subprocess.run(f"ping -c 1 -W 1 {ip} 2>/dev/null", shell=True)
                if result.returncode != 0:
                    self.isolated_ips.remove(ip)
            except:
                pass
    
    def _cleanup(self):
        """Limpa regras antigas"""
        while self.is_running:
            time.sleep(3600)  # A cada hora
            # Limpar regras de rate limiting antigas
            self.rate_limits.clear()
    
    def unisolate_machine(self, ip):
        """Remove isolamento de uma máquina"""
        if ip in self.isolated_ips:
            try:
                subprocess.run(f"sudo iptables -D INPUT -s {ip} -j DROP", shell=True)
                subprocess.run(f"sudo iptables -D OUTPUT -d {ip} -j DROP", shell=True)
                subprocess.run(f"sudo iptables -D FORWARD -s {ip} -j DROP", shell=True)
                self.isolated_ips.remove(ip)
                self._log(f"🔓 Máquina {ip} desisolada", "success")
                return True
            except:
                pass
        return False
    
    def get_stats(self):
        return {
            "isolated_machines": len(self.isolated_ips),
            "rate_limited_ips": len(self.connection_blacklist),
            "active_limits": len(self.rate_limits)
        }
    
    def _log(self, msg, level="info"):
        if self.callback:
            self.callback({"type": "log", "message": f"[PROACTIVE] {msg}", "level": level})
        print(f"[PROACTIVE] {msg}")
