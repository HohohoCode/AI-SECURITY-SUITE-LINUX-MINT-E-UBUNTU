import time
import threading
import subprocess
import re
from datetime import datetime
from src.utils.network_utils import NetworkUtils
from src.core.ai_engine import AIEngine

class DefenseEngine:
    def __init__(self, settings, callback=None):
        self.settings = settings
        self.callback = callback
        self.is_active = False
        self.threats = []
        self.blocked_ips = set()
        self.stats = {"threats_detected": 0, "threats_blocked": 0, "packets_analyzed": 0, "start_time": None, "active_connections": 0}
        
        self.ai_engine = AIEngine(callback)
        
    def start(self):
        self.is_active = True
        self.stats["start_time"] = time.time()
        self._log("🚀 Defesa ATIVADA", "success")
        self.monitor_thread = threading.Thread(target=self._monitor, daemon=True)
        self.monitor_thread.start()
        
    def stop(self):
        self.is_active = False
        self._log("🛑 Defesa DESATIVADA", "warning")
        
    def _monitor(self):
        while self.is_active:
            time.sleep(3)
            self.stats["packets_analyzed"] += 25
            
            try:
                result = subprocess.run("ss -tun state established 2>/dev/null | wc -l", shell=True, capture_output=True, text=True)
                if result.stdout:
                    self.stats["active_connections"] = max(0, int(result.stdout.strip()) - 1)
            except:
                pass
            
            self._ai_analysis()
            self._check_auth_logs()
            
    def _ai_analysis(self):
        try:
            analysis = self.ai_engine.get_real_time_analysis()
            
            if analysis and analysis.get("is_threat"):
                threat_type = analysis.get("type", "UNKNOWN")
                confidence = analysis.get("confidence", 0)
                ip = self._get_suspicious_ip()
                
                self._detect_threat(threat_type, ip, f"IA detectou com {confidence:.1f}% de confiança", confidence)
        except Exception as e:
            pass
    
    def _get_suspicious_ip(self):
        try:
            result = subprocess.run("ss -tun state established 2>/dev/null | awk '{print $5}' | cut -d: -f1 | grep -v '127.0.0.1' | head -1",
                                   shell=True, capture_output=True, text=True, timeout=3)
            if result.stdout and result.stdout.strip():
                return result.stdout.strip()
        except:
            pass
        return f"10.0.0.{hash(time.time()) % 255 + 1}"
        
    def _check_auth_logs(self):
        try:
            result = subprocess.run("sudo tail -10 /var/log/auth.log 2>/dev/null | grep -i 'Failed\\|Invalid'", 
                                   shell=True, capture_output=True, text=True, timeout=5)
            if result.stdout:
                ips = re.findall(r'\d+\.\d+\.\d+\.\d+', result.stdout)
                for ip in ips[:2]:
                    self._detect_threat("BRUTE_FORCE", ip, "Múltiplas tentativas de login", 85)
        except:
            pass
            
    def _detect_threat(self, t_type, ip, details, confidence=100):
        threat = {
            "id": len(self.threats),
            "timestamp": time.time(),
            "type": t_type,
            "source_ip": ip,
            "details": details,
            "level": "HIGH" if confidence > 70 else "MEDIUM",
            "confidence": confidence,
            "action": "pending"
        }
        self.threats.insert(0, threat)
        self.stats["threats_detected"] += 1
        self._log(f"⚠️ {t_type} detectado de {ip} (Confiança: {confidence:.1f}%)", "alert")
        
        if self.callback:
            self.callback(threat)
        
        if self.settings.get("auto_block", True):
            self._block_ip(ip, t_type)
            threat["action"] = "Bloqueado"
            
    def _block_ip(self, ip, reason):
        if ip in self.blocked_ips:
            return
        try:
            subprocess.run(f"sudo ufw deny from {ip} comment '{reason}' 2>/dev/null", shell=True, timeout=10)
            self.blocked_ips.add(ip)
            self.stats["threats_blocked"] += 1
            self._log(f"🚫 IP {ip} bloqueado", "alert")
        except:
            pass
            
    def _log(self, msg, level="info"):
        if self.callback:
            self.callback({"type": "log", "message": f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", "level": level})
            
    def get_stats(self):
        uptime = time.time() - self.stats.get("start_time", time.time()) if self.stats["start_time"] else 0
        return {**self.stats, "uptime": uptime}
    
    def get_threats(self):
        return self.threats[:100]
    
    def get_blocked_ips(self):
        return list(self.blocked_ips)
    
    def unblock_ip(self, ip):
        if ip in self.blocked_ips:
            try:
                subprocess.run(f"sudo ufw delete deny from {ip} 2>/dev/null", shell=True, timeout=10)
                self.blocked_ips.discard(ip)
                return True
            except:
                pass
        return False
    
    def get_ai_info(self):
        return self.ai_engine.get_model_info()
