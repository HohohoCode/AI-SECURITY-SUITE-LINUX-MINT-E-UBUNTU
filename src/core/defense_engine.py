import time
import threading
import subprocess
import re
from datetime import datetime
from src.utils.network_utils import NetworkUtils
from src.utils.firewall_utils import FirewallUtils
from src.core.ai_engine import AIEngine

class DefenseEngine:
    def __init__(self, settings, callback=None):
        self.settings = settings
        self.callback = callback
        self.is_active = True
        
        self.threats = []
        self.blocked_ips = set()
        self.counter_attacks = []
        self.max_history = 100
        
        self.stats = {
            "threats_detected": 0,
            "threats_blocked": 0,
            "packets_analyzed": 0,
            "start_time": time.time(),
            "active_connections": 0
        }
        
        self.ai_engine = AIEngine(self._handle_ai_event)
        self._activate_firewall()
        
        self.monitor_thread = threading.Thread(target=self._monitor_packets, daemon=True)
        self.monitor_thread.start()
        
        self._log("🛡️ Defesa TOTAL ativada", "success")
    
    def _is_local_ip(self, ip):
        """Verifica se o IP é da rede local (não deve ser bloqueado)"""
        if not ip:
            return True
        
        # Redes privadas
        private_ranges = [
            '10.',           # 10.0.0.0/8
            '192.168.',      # 192.168.0.0/16
            '172.16.', '172.17.', '172.18.', '172.19.',
            '172.20.', '172.21.', '172.22.', '172.23.',
            '172.24.', '172.25.', '172.26.', '172.27.',
            '172.28.', '172.29.', '172.30.', '172.31.',  # 172.16.0.0/12
            '127.',          # localhost
            '0.',            # 0.0.0.0/8
            '169.254.'       # link-local
        ]
        
        for private in private_ranges:
            if ip.startswith(private):
                return True
        return False
    
    def _monitor_packets(self):
        last_rx = 0
        last_tx = 0
        counter = 0
        
        while self.is_active:
            try:
                result = subprocess.run("cat /proc/net/dev | grep -E 'eth0|wlan0|enp|wl' | head -1", 
                                       shell=True, capture_output=True, text=True, timeout=3)
                if result.stdout:
                    parts = result.stdout.strip().split()
                    if len(parts) >= 10:
                        rx_bytes = int(parts[1])
                        tx_bytes = int(parts[9])
                        
                        if last_rx > 0:
                            rx_packets = (rx_bytes - last_rx) // 1500
                            tx_packets = (tx_bytes - last_tx) // 1500
                            self.stats["packets_analyzed"] += max(0, rx_packets + tx_packets)
                        
                        last_rx = rx_bytes
                        last_tx = tx_bytes
                
                result = subprocess.run("ss -tun state established 2>/dev/null | wc -l",
                                       shell=True, capture_output=True, text=True, timeout=3)
                if result.stdout:
                    conn_count = int(result.stdout.strip())
                    self.stats["active_connections"] = max(0, conn_count - 1)
                
                time.sleep(10)
                
                counter += 1
                if counter >= 60:
                    self._cleanup_history()
                    counter = 0
                    
            except Exception as e:
                time.sleep(10)
    
    def _cleanup_history(self):
        if len(self.threats) > self.max_history:
            self.threats = self.threats[:self.max_history]
        if len(self.counter_attacks) > self.max_history:
            self.counter_attacks = self.counter_attacks[:self.max_history]
    
    def _activate_firewall(self):
        try:
            FirewallUtils.enable()
            self._log("🔥 Firewall ativado", "success")
        except:
            pass
    
    def _handle_ai_event(self, event):
        if event.get("type") == "threat":
            threat = event.get("threat")
            self._process_threat(threat)
        elif event.get("type") == "log":
            if self.callback:
                self.callback({"type": "log", "message": event.get("message")})
    
    def _process_threat(self, threat):
        ip = threat.get("source_ip")
        t_type = threat.get("type")
        
        # NÃO BLOQUEAR IPS DE REDE LOCAL
        if self._is_local_ip(ip):
            self._log(f"⚠️ IP local {ip} ignorado (não será bloqueado)", "warning")
            return
        
        if ip in self.blocked_ips:
            return
        
        threat["id"] = len(self.threats)
        threat["action"] = "pending"
        self.threats.insert(0, threat)
        self.stats["threats_detected"] += 1
        
        if self.callback:
            self.callback(threat)
        
        if self.settings.get("auto_block", True):
            self._block_ip(ip, t_type)
    
    def _block_ip(self, ip, reason):
        # NÃO BLOQUEAR IPS DE REDE LOCAL
        if self._is_local_ip(ip):
            self._log(f"⚠️ IP local {ip} ignorado - não será bloqueado", "warning")
            return False
        
        if ip in self.blocked_ips:
            return True
        
        success = FirewallUtils.block_ip(ip, reason)
        if success:
            self.blocked_ips.add(ip)
            self.stats["threats_blocked"] += 1
            self._log(f"🚫 IP {ip} bloqueado - {reason}", "alert")
            self._register_counter_attack(ip, reason)
            return True
        return False
    
    def _register_counter_attack(self, ip, threat_type):
        if not ip or self._is_local_ip(ip):
            return
            
        info = []
        whois = NetworkUtils.get_whois(ip)
        if whois and whois != "N/A":
            info.append(f"WHOIS: {whois[:100]}")
        geo = NetworkUtils.get_geolocation(ip)
        if geo and geo != "N/A":
            info.append(f"📍 Geolocalização: {geo}")
        info.append(f"✅ IP {ip} bloqueado automaticamente")
        
        counter = {
            "ip": ip,
            "threat": threat_type,
            "info": info,
            "timestamp": time.time()
        }
        self.counter_attacks.insert(0, counter)
        
        if len(self.counter_attacks) > self.max_history:
            self.counter_attacks = self.counter_attacks[:self.max_history]
        
        if self.callback:
            self.callback({"type": "counter_attack", **counter})
    
    def _log(self, msg, level="info"):
        if self.callback:
            self.callback({"type": "log", "message": f"[{time.strftime('%H:%M:%S')}] {msg}", "level": level})
    
    def get_stats(self):
        self.stats["uptime"] = time.time() - self.stats["start_time"]
        return self.stats
    
    def get_threats(self):
        return self.threats[:100]
    
    def get_counter_attacks(self):
        return self.counter_attacks[:100]
    
    def get_blocked_ips(self):
        return list(self.blocked_ips)
    
    def unblock_ip(self, ip):
        if ip in self.blocked_ips:
            success = FirewallUtils.unblock_ip(ip)
            if success:
                self.blocked_ips.discard(ip)
                self._log(f"🔓 IP {ip} desbloqueado", "info")
                return True
        return False
    
    def reset_firewall(self):
        success = FirewallUtils.reset()
        if success:
            self.blocked_ips.clear()
            self._log("🔄 Firewall resetado", "success")
        return success
