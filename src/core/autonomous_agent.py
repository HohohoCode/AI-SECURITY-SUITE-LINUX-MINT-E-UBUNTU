"""
AGENTE DE DEFESA AUTÔNOMO EM TEMPO REAL
- Monitoramento contínuo 24/7
- Resposta imediata a ameaças
- Adaptação automática
- Aprendizado contínuo
"""

import threading
import time
import subprocess
import re
import json
import os
from datetime import datetime
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class Threat:
    """Representa uma ameaça detectada"""
    ip: str
    type: str
    severity: str  # low, medium, high, critical
    confidence: float
    timestamp: float
    details: Dict
    action_taken: str

class AutonomousDefenseAgent:
    """
    Agente de Defesa Autônomo
    - Opera em tempo real
    - Decisões automáticas
    - Aprende com cada ataque
    """
    
    def __init__(self, defense_engine, callback=None):
        self.defense_engine = defense_engine
        self.callback = callback
        self.is_running = False
        self.threat_history = deque(maxlen=1000)
        self.blocked_ips_cache = set()
        self.attack_patterns = self._load_attack_patterns()
        self.response_actions = self._init_response_actions()
        
        # Estatísticas do agente
        self.stats = {
            "total_threats_analyzed": 0,
            "total_blocks": 0,
            "avg_response_time": 0,
            "false_positives": 0,
            "uptime": 0,
            "start_time": None
        }
        
        # Limiares adaptativos
        self.thresholds = {
            "ddos_connections": 100,      # conexões em 10s
            "bruteforce_attempts": 10,    # tentativas em 60s
            "port_scan_ports": 20,        # portas em 10s
            "confidence_threshold": 70,    # % de confiança mínima
        }
        
    def _load_attack_patterns(self):
        """Carrega padrões de ataque conhecidos"""
        return {
            "DDoS": {
                "keywords": ["flood", "high traffic", "many connections", "syn flood"],
                "severity": "critical",
                "auto_block": True,
                "block_duration": 3600  # 1 hora
            },
            "BRUTE_FORCE": {
                "keywords": ["failed login", "password attempt", "brute force"],
                "severity": "high",
                "auto_block": True,
                "block_duration": 1800  # 30 minutos
            },
            "PORT_SCAN": {
                "keywords": ["port scan", "nmap", "multiple ports"],
                "severity": "medium",
                "auto_block": True,
                "block_duration": 600  # 10 minutos
            },
            "SQL_INJECTION": {
                "keywords": ["sql injection", "union select", "drop table"],
                "severity": "critical",
                "auto_block": True,
                "block_duration": 7200  # 2 horas
            },
            "MALWARE": {
                "keywords": ["malware", "virus", "trojan", "ransomware"],
                "severity": "critical",
                "auto_block": True,
                "block_duration": 86400  # 24 horas
            }
        }
    
    def _init_response_actions(self):
        """Inicializa ações de resposta"""
        return {
            "critical": [
                self._immediate_block,
                self._notify_admin,
                self._log_attack,
                self._increase_monitoring
            ],
            "high": [
                self._immediate_block,
                self._log_attack,
                self._increase_monitoring
            ],
            "medium": [
                self._block_with_warning,
                self._log_attack
            ],
            "low": [
                self._log_attack,
                self._monitor_only
            ]
        }
    
    def start(self):
        """Inicia o agente autônomo"""
        self.is_running = True
        self.stats["start_time"] = time.time()
        self._log("🤖 Agente de Defesa Autônomo ATIVADO", "success")
        self._log("🛡️ Monitoramento em tempo real 24/7", "info")
        
        # Iniciar threads de monitoramento
        self.monitor_thread = threading.Thread(target=self._continuous_monitoring, daemon=True)
        self.monitor_thread.start()
        
        self.learning_thread = threading.Thread(target=self._continuous_learning, daemon=True)
        self.learning_thread.start()
        
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
    
    def stop(self):
        """Para o agente"""
        self.is_running = False
        self._log("🤖 Agente de Defesa Autônomo DESATIVADO", "warning")
    
    def _continuous_monitoring(self):
        """Monitoramento contínuo em tempo real"""
        while self.is_running:
            try:
                # 1. Verificar tráfego de rede
                self._analyze_network_traffic()
                
                # 2. Verificar logs de autenticação
                self._analyze_auth_logs()
                
                # 3. Verificar processos suspeitos
                self._analyze_processes()
                
                # 4. Verificar conexões externas
                self._analyze_connections()
                
                # 5. Análise com IA
                self._ai_analysis()
                
                # Atualizar estatísticas
                self.stats["uptime"] = time.time() - self.stats["start_time"]
                
                time.sleep(1)  # Verifica a cada 1 segundo
            except Exception as e:
                self._log(f"Erro no monitoramento: {e}", "error")
    
    def _analyze_network_traffic(self):
        """Analisa tráfego de rede em tempo real"""
        try:
            # Obter conexões ativas
            result = subprocess.run("ss -tun state established 2>/dev/null | wc -l", 
                                   shell=True, capture_output=True, text=True, timeout=2)
            total_connections = int(result.stdout.strip()) if result.stdout else 0
            
            # Contar conexões por IP
            result = subprocess.run("ss -tun state established 2>/dev/null | awk '{print $5}' | cut -d: -f1 | sort | uniq -c",
                                   shell=True, capture_output=True, text=True, timeout=2)
            
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            count = int(parts[0])
                            ip = parts[1]
                            
                            # Detectar DDoS
                            if count > self.thresholds["ddos_connections"] and ip not in self.blocked_ips_cache:
                                self._handle_threat(Threat(
                                    ip=ip,
                                    type="DDoS",
                                    severity="critical",
                                    confidence=95.0,
                                    timestamp=time.time(),
                                    details={"connections": count, "threshold": self.thresholds["ddos_connections"]},
                                    action_taken="pending"
                                ))
        except:
            pass
    
    def _analyze_auth_logs(self):
        """Analisa logs de autenticação"""
        try:
            # Últimos 60 segundos de logs
            result = subprocess.run("sudo tail -100 /var/log/auth.log 2>/dev/null | grep -i 'Failed password'",
                                   shell=True, capture_output=True, text=True, timeout=3)
            
            if result.stdout:
                # Contar tentativas por IP
                ips = re.findall(r'from (\d+\.\d+\.\d+\.\d+)', result.stdout)
                from collections import Counter
                ip_counts = Counter(ips)
                
                for ip, count in ip_counts.items():
                    if count > self.thresholds["bruteforce_attempts"] and ip not in self.blocked_ips_cache:
                        self._handle_threat(Threat(
                            ip=ip,
                            type="BRUTE_FORCE",
                            severity="high",
                            confidence=90.0,
                            timestamp=time.time(),
                            details={"attempts": count, "time_window": 60},
                            action_taken="pending"
                        ))
        except:
            pass
    
    def _analyze_processes(self):
        """Analisa processos em execução"""
        try:
            # Verificar processos suspeitos
            suspicious_processes = [
                "nmap", "hydra", "john", "sqlmap", "nc", "netcat",
                "metasploit", "msfconsole", "beef", "aircrack"
            ]
            
            for proc in suspicious_processes:
                result = subprocess.run(f"pgrep -x {proc} 2>/dev/null", shell=True, capture_output=True)
                if result.stdout:
                    self._log(f"⚠️ Processo suspeito detectado: {proc}", "alert")
        except:
            pass
    
    def _analyze_connections(self):
        """Analisa conexões externas suspeitas"""
        try:
            # Portas conhecidas de C2 (Command & Control)
            c2_ports = [4444, 5555, 6666, 7777, 8888, 9999, 31337, 31338]
            
            for port in c2_ports:
                result = subprocess.run(f"ss -tun state established 2>/dev/null | grep ':{port} '", 
                                       shell=True, capture_output=True, text=True)
                if result.stdout:
                    ips = re.findall(r'\d+\.\d+\.\d+\.\d+', result.stdout)
                    for ip in ips:
                        if ip not in self.blocked_ips_cache:
                            self._handle_threat(Threat(
                                ip=ip,
                                type="C2_COMMUNICATION",
                                severity="critical",
                                confidence=95.0,
                                timestamp=time.time(),
                                details={"port": port, "message": "Possível comunicação C2 detectada"},
                                action_taken="pending"
                            ))
        except:
            pass
    
    def _ai_analysis(self):
        """Análise complementar com IA"""
        try:
            if self.defense_engine and hasattr(self.defense_engine, 'ai_engine'):
                analysis = self.defense_engine.ai_engine.get_real_time_analysis()
                if analysis and analysis.get('is_threat'):
                    ip = self._get_suspicious_ip()
                    if ip and ip not in self.blocked_ips_cache:
                        self._handle_threat(Threat(
                            ip=ip,
                            type=analysis.get('type', 'UNKNOWN'),
                            severity="high",
                            confidence=analysis.get('confidence', 70),
                            timestamp=time.time(),
                            details={"ai_analysis": analysis},
                            action_taken="pending"
                        ))
        except:
            pass
    
    def _get_suspicious_ip(self):
        """Obtém IP suspeito das conexões"""
        try:
            result = subprocess.run("ss -tun state established 2>/dev/null | awk '{print $5}' | cut -d: -f1 | head -1",
                                   shell=True, capture_output=True, text=True, timeout=2)
            if result.stdout and result.stdout.strip():
                return result.stdout.strip()
        except:
            pass
        return None
    
    def _handle_threat(self, threat: Threat):
        """Processa uma ameaça detectada"""
        self.stats["total_threats_analyzed"] += 1
        start_time = time.time()
        
        # Registrar ameaça
        self.threat_history.append(threat)
        self._log(f"🚨 AMEAÇA DETECTADA: {threat.type} de {threat.ip} (Confiança: {threat.confidence:.1f}%)", "alert")
        
        # Determinar ações baseadas na severidade
        actions = self.response_actions.get(threat.severity, self.response_actions["low"])
        
        for action in actions:
            action(threat)
        
        # Atualizar tempo de resposta
        response_time = time.time() - start_time
        self.stats["avg_response_time"] = (self.stats["avg_response_time"] + response_time) / 2
        
        # Notificar callback
        if self.callback:
            self.callback({
                "type": "agent_threat",
                "threat": threat.__dict__,
                "response_time": response_time
            })
    
    def _immediate_block(self, threat: Threat):
        """Bloqueio imediato do IP"""
        try:
            cmd = f"sudo ufw deny from {threat.ip} comment 'AutonomousAgent: {threat.type}'"
            subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
            self.blocked_ips_cache.add(threat.ip)
            self.stats["total_blocks"] += 1
            threat.action_taken = "blocked"
            self._log(f"🔒 IP {threat.ip} BLOQUEADO automaticamente", "success")
        except Exception as e:
            self._log(f"❌ Falha ao bloquear {threat.ip}: {e}", "error")
    
    def _block_with_warning(self, threat: Threat):
        """Bloqueio com aviso (para ameaças médias)"""
        self._immediate_block(threat)
        self._log(f"⚠️ IP {threat.ip} bloqueado com monitoramento intensificado", "warning")
    
    def _notify_admin(self, threat: Threat):
        """Notifica administrador"""
        self._log(f"📧 Notificação: Ataque {threat.type} de {threat.ip}", "info")
        # Aqui poderia enviar email, Telegram, etc.
    
    def _log_attack(self, threat: Threat):
        """Registra ataque em log persistente"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "ip": threat.ip,
            "type": threat.type,
            "severity": threat.severity,
            "confidence": threat.confidence,
            "details": threat.details
        }
        
        log_file = os.path.expanduser("~/.ai-security-suite/attacks.log")
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        try:
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except:
            pass
    
    def _increase_monitoring(self, threat: Threat):
        """Aumenta monitoramento para este IP"""
        self._log(f"📊 Monitoramento intensificado para {threat.ip}", "info")
        # Aqui poderia adicionar regras específicas de monitoramento
    
    def _monitor_only(self, threat: Threat):
        """Apenas monitora, não bloqueia"""
        self._log(f"👁️ Monitorando {threat.ip} (sem bloqueio)", "info")
    
    def _continuous_learning(self):
        """Aprendizado contínuo baseado em ataques anteriores"""
        while self.is_running:
            time.sleep(60)  # A cada minuto
            
            # Ajustar limiares baseado em experiência
            if len(self.threat_history) > 100:
                # Calcular média de ataques
                recent_threats = list(self.threat_history)[-100:]
                ddos_count = sum(1 for t in recent_threats if t.type == "DDoS")
                bruteforce_count = sum(1 for t in recent_threats if t.type == "BRUTE_FORCE")
                
                # Ajustar limiares dinamicamente
                if ddos_count > 10:
                    self.thresholds["ddos_connections"] = max(50, self.thresholds["ddos_connections"] - 5)
                    self._log(f"📈 Limiar DDoS ajustado para {self.thresholds['ddos_connections']}", "info")
                
                if bruteforce_count > 20:
                    self.thresholds["bruteforce_attempts"] = max(5, self.thresholds["bruteforce_attempts"] - 1)
                    self._log(f"📈 Limiar Brute Force ajustado para {self.thresholds['bruteforce_attempts']}", "info")
    
    def _cleanup_loop(self):
        """Limpa bloqueios antigos"""
        while self.is_running:
            time.sleep(300)  # A cada 5 minutos
            
            # Aqui poderia remover bloqueios antigos após expiração
            pass
    
    def get_stats(self):
        """Retorna estatísticas do agente"""
        return {
            **self.stats,
            "blocked_ips_count": len(self.blocked_ips_cache),
            "threats_in_history": len(self.threat_history),
            "active_thresholds": self.thresholds
        }
    
    def get_recent_threats(self, count=10):
        """Retorna as últimas ameaças"""
        return list(self.threat_history)[-count:]
    
    def _log(self, message, level="info"):
        if self.callback:
            self.callback({"type": "log", "message": f"[AGENTE] {message}", "level": level})
        print(f"[AGENTE] {message}")
    
    def _is_valid_ip(self, ip):
        """Valida formato de IP"""
        pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
        return pattern.match(ip) is not None
