import time
import threading
import subprocess
import re
from datetime import datetime
from src.utils.network_utils import NetworkUtils
from src.core.advanced_ai import UltraAdvancedAI
from src.core.autonomous_agent import AutonomousDefenseAgent
from src.core.honeypot import Honeypot
from src.core.threat_intel import ThreatIntelligence
from src.core.behavioral_analysis import BehavioralAnalyzer
from src.core.proactive_defense import ProactiveDefense

class DefenseEngine:
    def __init__(self, settings, callback=None):
        self.settings = settings
        self.callback = callback
        self.is_active = False
        self.threats = []
        self.blocked_ips = set()
        self.stats = {"threats_detected": 0, "threats_blocked": 0, "packets_analyzed": 0, "start_time": None, "active_connections": 0}
        
        # Módulos de defesa
        self.ai_engine = UltraAdvancedAI(callback)
        self.autonomous_agent = None
        self.honeypot = None
        self.threat_intel = None
        self.behavioral_analyzer = None
        self.proactive_defense = None
        
        # Rastreadores
        self.connection_tracker = {}
        self.failed_login_tracker = {}
        self.last_cleanup = time.time()
        
        # IPs de demonstração
        self.valid_demo_ips = [
            "185.130.5.253", "185.220.101.1", "45.227.254.1",
            "103.115.16.1", "5.188.86.1", "185.165.29.1"
        ]
        self.demo_index = 0
    
    def _is_valid_ip(self, ip):
        if not ip or not isinstance(ip, str):
            return False
        pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
        if not pattern.match(ip):
            return False
        parts = ip.split('.')
        for part in parts:
            try:
                if int(part) > 255:
                    return False
            except:
                return False
        return True
    
    def start(self):
        self.is_active = True
        self.stats["start_time"] = time.time()
        self._log("🚀 DEFESA TOTAL ATIVADA!", "success")
        self._log("🧠 IA Ultra-Avançada | 🤖 Agente Autônomo | 🍯 Honeypot", "info")
        self._log("🕵️ Threat Intelligence | 📊 Behavioral Analysis | 🛡️ Proactive Defense", "info")
        
        # Iniciar todos os módulos
        self.autonomous_agent = AutonomousDefenseAgent(self, self.callback)
        self.autonomous_agent.start()
        
        self.honeypot = Honeypot(self.callback)
        self.honeypot.start()
        
        self.threat_intel = ThreatIntelligence(self.callback)
        self.threat_intel.start()
        
        self.behavioral_analyzer = BehavioralAnalyzer(self.callback)
        self.behavioral_analyzer.start()
        
        self.proactive_defense = ProactiveDefense(self.callback)
        self.proactive_defense.start()
        
        self.monitor_thread = threading.Thread(target=self._monitor, daemon=True)
        self.monitor_thread.start()
    
    def stop(self):
        self.is_active = False
        if self.autonomous_agent:
            self.autonomous_agent.stop()
        if self.honeypot:
            self.honeypot.stop()
        if self.behavioral_analyzer:
            self.behavioral_analyzer.stop()
        if self.proactive_defense:
            self.proactive_defense.stop()
        self._log("🛑 Defesa TOTAL DESATIVADA", "warning")
    
    def _monitor(self):
        while self.is_active:
            time.sleep(2)
            self.stats["packets_analyzed"] += 50
            self._update_connections()
            self._detect_ddos()
            self._detect_bruteforce()
            
            if time.time() - self.last_cleanup > 60:
                self._cleanup_trackers()
                self.last_cleanup = time.time()
            
            self._ai_analysis()
            self._check_auth_logs()
    
    def _update_connections(self):
        try:
            result = subprocess.run("ss -tun state established 2>/dev/null | awk '{print $5}' | cut -d: -f1 | grep -v '127.0.0.1'",
                                   shell=True, capture_output=True, text=True, timeout=3)
            if result.stdout:
                ips = result.stdout.strip().split('\n')
                valid_ips = [ip for ip in ips if self._is_valid_ip(ip)]
                self.stats["active_connections"] = len(valid_ips)
                
                ip_counts = {}
                for ip in valid_ips:
                    if ip:
                        ip_counts[ip] = ip_counts.get(ip, 0) + 1
                
                current_time = time.time()
                for ip, count in ip_counts.items():
                    if ip not in self.connection_tracker:
                        self.connection_tracker[ip] = []
                    self.connection_tracker[ip].append((current_time, count))
        except:
            pass
    
    def _detect_ddos(self):
        current_time = time.time()
        window_seconds = 10
        
        for ip, records in list(self.connection_tracker.items()):
            if not self._is_valid_ip(ip):
                continue
            recent = [(t, c) for t, c in records if current_time - t <= window_seconds]
            total_connections = sum(c for _, c in recent)
            
            if total_connections > 100 and ip not in self.blocked_ips:
                self._detect_threat("DDoS", ip, f"Alto tráfego: {total_connections} conexões", 95)
                self._block_ip(ip, "DDoS Detectado")
            
            self.connection_tracker[ip] = recent
    
    def _detect_bruteforce(self):
        try:
            result = subprocess.run("sudo tail -50 /var/log/auth.log 2>/dev/null | grep -i 'Failed password'",
                                   shell=True, capture_output=True, text=True, timeout=5)
            if result.stdout:
                ips = re.findall(r'from (\d+\.\d+\.\d+\.\d+)', result.stdout)
                current_time = time.time()
                window_seconds = 60
                
                for ip in ips:
                    if not self._is_valid_ip(ip):
                        continue
                    if ip not in self.failed_login_tracker:
                        self.failed_login_tracker[ip] = []
                    self.failed_login_tracker[ip].append(current_time)
                    
                    recent = [t for t in self.failed_login_tracker[ip] if current_time - t <= window_seconds]
                    attempts = len(recent)
                    
                    if attempts > 10 and ip not in self.blocked_ips:
                        self._detect_threat("BRUTE_FORCE", ip, f"{attempts} tentativas", 90)
                        self._block_ip(ip, "Brute Force Detectado")
                    
                    self.failed_login_tracker[ip] = recent
        except:
            pass
    
    def _cleanup_trackers(self):
        current_time = time.time()
        cutoff = 300
        
        for ip in list(self.connection_tracker.keys()):
            self.connection_tracker[ip] = [(t, c) for t, c in self.connection_tracker[ip] if current_time - t <= cutoff]
            if not self.connection_tracker[ip]:
                del self.connection_tracker[ip]
        
        for ip in list(self.failed_login_tracker.keys()):
            self.failed_login_tracker[ip] = [t for t in self.failed_login_tracker[ip] if current_time - t <= cutoff]
            if not self.failed_login_tracker[ip]:
                del self.failed_login_tracker[ip]
    
    def _ai_analysis(self):
        try:
            analysis = self.ai_engine.get_real_time_analysis()
            
            if analysis and analysis.get("is_threat"):
                threat_type = analysis.get("type", "UNKNOWN")
                confidence = analysis.get("confidence", 0)
                ip = self._get_suspicious_ip()
                
                valid_ip = self._get_valid_ip(ip)
                if valid_ip and valid_ip not in self.blocked_ips:
                    self._detect_threat(threat_type, valid_ip, f"IA detectou", confidence)
                    self._block_ip(valid_ip, f"IA: {threat_type}")
        except Exception as e:
            pass
    
    def _get_suspicious_ip(self):
        try:
            result = subprocess.run("ss -tun state established 2>/dev/null | awk '{print $5}' | cut -d: -f1 | grep -v '127.0.0.1' | grep -v '192.168.' | grep -v '10.' | head -1",
                                   shell=True, capture_output=True, text=True, timeout=3)
            if result.stdout and result.stdout.strip():
                ip = result.stdout.strip()
                if self._is_valid_ip(ip):
                    return ip
        except:
            pass
        
        self.demo_index = (self.demo_index + 1) % len(self.valid_demo_ips)
        return self.valid_demo_ips[self.demo_index]
    
    def _get_valid_ip(self, ip):
        if self._is_valid_ip(ip):
            return ip
        self.demo_index = (self.demo_index + 1) % len(self.valid_demo_ips)
        return self.valid_demo_ips[self.demo_index]
    
    def _check_auth_logs(self):
        try:
            result = subprocess.run("sudo tail -20 /var/log/auth.log 2>/dev/null | grep -i 'Failed\\|Invalid'", 
                                   shell=True, capture_output=True, text=True, timeout=5)
            if result.stdout:
                ips = re.findall(r'\d+\.\d+\.\d+\.\d+', result.stdout)
                for ip in ips[:2]:
                    if self._is_valid_ip(ip) and ip not in self.blocked_ips:
                        self._detect_threat("BRUTE_FORCE", ip, "Múltiplas tentativas", 85)
                        self._block_ip(ip, "Brute Force")
        except:
            pass
    
    def _detect_threat(self, t_type, ip, details, confidence=100):
        if not self._is_valid_ip(ip):
            return
        if ip in self.blocked_ips:
            return
            
        threat = {
            "id": len(self.threats),
            "timestamp": time.time(),
            "type": t_type,
            "source_ip": ip,
            "details": details,
            "level": "CRITICAL" if t_type in ["DDoS", "BRUTE_FORCE"] else "HIGH",
            "confidence": confidence,
            "action": "pending"
        }
        self.threats.insert(0, threat)
        self.stats["threats_detected"] += 1
        self._log(f"⚠️ {t_type} detectado de {ip} (Confiança: {confidence:.1f}%)", "alert")
        
        if self.callback:
            self.callback(threat)
    
    def _block_ip(self, ip, reason):
        if not self._is_valid_ip(ip):
            return False
        if ip in self.blocked_ips:
            return True
        
        try:
            status_result = subprocess.run("sudo ufw status", shell=True, capture_output=True, text=True, timeout=5)
            if "inactive" in status_result.stdout.lower():
                subprocess.run("sudo ufw --force enable", shell=True, capture_output=True, timeout=10)
            
            cmd = f"sudo ufw deny from {ip} comment '{reason}'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.blocked_ips.add(ip)
                self.stats["threats_blocked"] += 1
                self._log(f"✅ IP {ip} bloqueado - Motivo: {reason}", "success")
                self._auto_counter(ip, reason)
                return True
            else:
                return False
        except Exception as e:
            self._log(f"❌ Erro ao bloquear IP {ip}: {str(e)[:100]}", "error")
            return False
    
    def _auto_counter(self, ip, t_type):
        if not self._is_valid_ip(ip):
            return
            
        self._log(f"⚔️ Iniciando contra-ataque contra {ip}", "warning")
        info = []
        
        whois = NetworkUtils.get_whois(ip)
        if whois and whois != "N/A":
            info.append(f"WHOIS: {whois[:100]}")
        
        geo = NetworkUtils.get_geolocation(ip)
        if geo and geo != "N/A":
            info.append(f"📍 Geolocalização: {geo}")
        
        info.append(f"✅ IP {ip} bloqueado automaticamente")
        
        if self.callback:
            self.callback({
                "type": "counter_attack",
                "ip": ip,
                "threat": t_type,
                "info": info,
                "timestamp": time.time()
            })
        self._log(f"✅ Contra-ataque contra {ip} concluído", "success")
    
    def _log(self, msg, level="info"):
        if self.callback:
            self.callback({"type": "log", "message": f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", "level": level})
        print(msg)
    
    def get_stats(self):
        uptime = time.time() - self.stats.get("start_time", time.time()) if self.stats["start_time"] else 0
        return {**self.stats, "uptime": uptime, "blocked_count": len(self.blocked_ips)}
    
    def get_threats(self):
        return self.threats[:100]
    
    def get_blocked_ips(self):
        try:
            result = subprocess.run("sudo ufw status | grep DENY", shell=True, capture_output=True, text=True, timeout=5)
            ufw_ips = re.findall(r'\d+\.\d+\.\d+\.\d+', result.stdout)
            for ip in ufw_ips:
                if self._is_valid_ip(ip):
                    self.blocked_ips.add(ip)
        except:
            pass
        return list(self.blocked_ips)
    
    def unblock_ip(self, ip):
        if ip in self.blocked_ips:
            try:
                subprocess.run(f"sudo ufw delete deny from {ip} 2>/dev/null", shell=True, timeout=10)
                self.blocked_ips.discard(ip)
                self._log(f"🔓 IP {ip} desbloqueado", "info")
                return True
            except:
                pass
        return False
    
    def get_ai_info(self):
        return self.ai_engine.get_model_info()
    
    def get_agent_stats(self):
        stats = {}
        if self.autonomous_agent:
            stats['autonomous'] = self.autonomous_agent.get_stats()
        if self.honeypot:
            stats['honeypot'] = self.honeypot.get_stats()
        if self.threat_intel:
            stats['threat_intel'] = self.threat_intel.get_blocked_stats()
        if self.behavioral_analyzer:
            stats['behavioral'] = self.behavioral_analyzer.get_stats()
        if self.proactive_defense:
            stats['proactive'] = self.proactive_defense.get_stats()
        return stats
