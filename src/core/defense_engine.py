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
        
        self.stats = {
            "threats_detected": 0,
            "threats_blocked": 0,
            "packets_analyzed": 0,
            "start_time": time.time(),
            "active_connections": 0,
            "last_packet_count": 0
        }
        
        self.ai_engine = AIEngine(self._handle_ai_event)
        self._activate_firewall()
        
        # Iniciar monitoramento de pacotes
        self.packet_counter = 0
        self.monitor_thread = threading.Thread(target=self._monitor_packets, daemon=True)
        self.monitor_thread.start()
        
        self._log("🛡️ Defesa TOTAL ativada", "success")
    
    def _monitor_packets(self):
        """Monitora pacotes de rede em tempo real"""
        last_rx = 0
        last_tx = 0
        
        while self.is_active:
            try:
                # Ler estatísticas de rede da interface ativa
                result = subprocess.run("cat /proc/net/dev | grep -E 'eth0|wlan0|enp|wl' | head -1", 
                                       shell=True, capture_output=True, text=True)
                if result.stdout:
                    # Extrair bytes recebidos e transmitidos
                    parts = result.stdout.strip().split()
                    if len(parts) >= 10:
                        rx_bytes = int(parts[1])  # bytes recebidos
                        tx_bytes = int(parts[9])  # bytes transmitidos
                        
                        # Calcular pacotes (aproximadamente 1 pacote = 1500 bytes)
                        if last_rx > 0:
                            rx_packets = (rx_bytes - last_rx) // 1500
                            tx_packets = (tx_bytes - last_tx) // 1500
                            self.packet_counter += max(0, rx_packets + tx_packets)
                            
                            # Atualizar estatísticas a cada 10 segundos
                            self.stats["packets_analyzed"] = self.packet_counter
                        
                        last_rx = rx_bytes
                        last_tx = tx_bytes
                
                # Também contar conexões como pacotes
                result = subprocess.run("ss -tun state established 2>/dev/null | wc -l",
                                       shell=True, capture_output=True, text=True)
                if result.stdout:
                    conn_count = int(result.stdout.strip())
                    self.stats["active_connections"] = max(0, conn_count - 1)
                
                time.sleep(5)
            except:
                pass
    
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
        if ip in self.blocked_ips:
            return
        
        success = FirewallUtils.block_ip(ip, reason)
        if success:
            self.blocked_ips.add(ip)
            self.stats["threats_blocked"] += 1
            self._log(f"🚫 IP {ip} bloqueado - {reason}", "alert")
            self._register_counter_attack(ip, reason)
    
    def _register_counter_attack(self, ip, threat_type):
        if not ip:
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
        
        if self.callback:
            self.callback({"type": "counter_attack", **counter})
    
    def _log(self, msg, level="info"):
        if self.callback:
            self.callback({"type": "log", "message": f"[{time.strftime('%H:%M:%S')}] {msg}", "level": level})
    
    def get_stats(self):
        # Atualizar conexões
        try:
            result = subprocess.run("ss -tun state established 2>/dev/null | wc -l", shell=True, capture_output=True, text=True)
            if result.stdout:
                self.stats["active_connections"] = max(0, int(result.stdout.strip()) - 1)
        except:
            pass
        
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
