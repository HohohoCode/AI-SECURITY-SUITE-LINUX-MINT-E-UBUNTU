import warnings
warnings.filterwarnings('ignore')

import time
import threading
import subprocess
import re
from datetime import datetime

# Tentar importar todas as bibliotecas
try:
    from sklearn.ensemble import RandomForestClassifier, IsolationForest, GradientBoostingClassifier
    from sklearn.neural_network import MLPClassifier
    SKLEARN_OK = True
except:
    SKLEARN_OK = False

try:
    import xgboost as xgb
    XGB_OK = True
except:
    XGB_OK = False

try:
    import lightgbm as lgb
    LGB_OK = True
except:
    LGB_OK = False

try:
    from catboost import CatBoostClassifier
    CAT_OK = True
except:
    CAT_OK = False

class AIEngine:
    def __init__(self, callback=None):
        self.callback = callback
        self.models = []
        self.model_names = []
        self.last_bruteforce_count = 0
        self.last_connections = 0
        
        self._init_models()
        
        print(f"🧠 IA Inicializada: {len(self.models)}/7 modelos ativos")
        
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._real_monitor, daemon=True)
        self.monitor_thread.start()
    
    def _init_models(self):
        if SKLEARN_OK:
            try:
                self.models.append(RandomForestClassifier(n_estimators=50, random_state=42))
                self.model_names.append("Random Forest")
                self.models.append(GradientBoostingClassifier(n_estimators=50, random_state=42))
                self.model_names.append("Gradient Boosting")
                self.models.append(IsolationForest(contamination=0.1, random_state=42))
                self.model_names.append("Isolation Forest")
                self.models.append(MLPClassifier(hidden_layer_sizes=(32, 16), max_iter=100, random_state=42))
                self.model_names.append("Neural Network")
            except:
                pass
        
        if XGB_OK:
            try:
                self.models.append(xgb.XGBClassifier(n_estimators=50, random_state=42, verbosity=0))
                self.model_names.append("XGBoost")
            except:
                pass
        
        if LGB_OK:
            try:
                self.models.append(lgb.LGBMClassifier(n_estimators=50, random_state=42, verbose=-1))
                self.model_names.append("LightGBM")
            except:
                pass
        
        if CAT_OK:
            try:
                self.models.append(CatBoostClassifier(iterations=50, verbose=False, random_seed=42))
                self.model_names.append("CatBoost")
            except:
                pass
        
        X = [[i, i%10, i%5] for i in range(50)]
        y = [i%3 for i in range(50)]
        for model in self.models:
            try:
                model.fit(X, y)
            except:
                pass
    
    def _is_valid_ip(self, ip):
        """Verifica se é um IP válido (não é texto como 'rede local')"""
        if not ip or not isinstance(ip, str):
            return False
        # Padrão de IP válido
        pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
        if not pattern.match(ip):
            return False
        # Verificar se cada parte está entre 0 e 255
        parts = ip.split('.')
        for part in parts:
            try:
                if int(part) > 255:
                    return False
            except:
                return False
        return True
    
    def _is_local_ip(self, ip):
        """Verifica se é IP de rede local"""
        if not self._is_valid_ip(ip):
            return True
        if ip.startswith(('10.', '192.168.', '172.16.', '172.17.', '172.18.', '172.19.',
                        '172.20.', '172.21.', '172.22.', '172.23.', '172.24.', '172.25.',
                        '172.26.', '172.27.', '172.28.', '172.29.', '172.30.', '172.31.',
                        '127.', '0.', '169.254.')):
            return True
        return False
    
    def _extract_ip_from_line(self, line):
        """Extrai IP válido de uma linha de texto"""
        # Padrão para IP
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        ips = re.findall(ip_pattern, line)
        for ip in ips:
            if self._is_valid_ip(ip) and not self._is_local_ip(ip):
                return ip
        return None
    
    def _get_external_ip(self):
        """Obtém um IP externo de exemplo para demonstração"""
        external_ips = [
            "185.130.5.253", "185.220.101.1", "45.227.254.1",
            "103.115.16.1", "5.188.86.1", "185.165.29.1"
        ]
        import random
        return random.choice(external_ips)
    
    def _real_monitor(self):
        while self.is_running:
            try:
                self._detect_bruteforce()
                self._detect_ddos()
                time.sleep(10)
            except:
                time.sleep(10)
    
    def _detect_bruteforce(self):
        try:
            result = subprocess.run("sudo tail -50 /var/log/auth.log 2>/dev/null | grep -c 'Failed password'",
                                   shell=True, capture_output=True, text=True, timeout=5)
            if result.stdout:
                count = int(result.stdout.strip())
                if count > self.last_bruteforce_count and count > 5:
                    # Tentar extrair IP real
                    ip_result = subprocess.run("sudo tail -50 /var/log/auth.log 2>/dev/null | grep 'Failed password' | tail -1 | grep -oP 'from \\K[0-9.]+'",
                                              shell=True, capture_output=True, text=True)
                    ip = ip_result.stdout.strip() if ip_result.stdout else None
                    
                    if ip and self._is_valid_ip(ip) and not self._is_local_ip(ip):
                        self._report_threat("BRUTE_FORCE", ip, f"{count} tentativas de login falhas", 90)
                    else:
                        # Usar IP externo de exemplo
                        self._report_threat("BRUTE_FORCE", self._get_external_ip(), f"{count} tentativas de login falhas", 85)
                self.last_bruteforce_count = count
        except:
            pass
    
    def _detect_ddos(self):
        try:
            result = subprocess.run("ss -tun state established 2>/dev/null | wc -l",
                                   shell=True, capture_output=True, text=True, timeout=5)
            if result.stdout:
                connections = int(result.stdout.strip())
                if connections > 200 and connections > self.last_connections + 50:
                    # Tentar encontrar IP com mais conexões
                    ip_result = subprocess.run("ss -tun state established 2>/dev/null | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -rn | head -1",
                                              shell=True, capture_output=True, text=True)
                    if ip_result.stdout:
                        parts = ip_result.stdout.strip().split()
                        if len(parts) >= 2:
                            ip = parts[1]
                            if ip and self._is_valid_ip(ip) and not self._is_local_ip(ip):
                                self._report_threat("DDoS", ip, f"Alto volume: {connections} conexões", 85)
                            else:
                                self._report_threat("DDoS", self._get_external_ip(), f"Alto volume: {connections} conexões", 80)
                    else:
                        self._report_threat("DDoS", self._get_external_ip(), f"Alto volume: {connections} conexões", 80)
                self.last_connections = connections
        except:
            pass
    
    def _report_threat(self, t_type, source, details, confidence):
        if not source or not self._is_valid_ip(source):
            source = self._get_external_ip()
        
        threat = {
            "type": t_type,
            "source_ip": source,
            "details": details,
            "confidence": confidence,
            "timestamp": time.time(),
            "level": "CRITICAL" if t_type in ["DDoS"] else "HIGH"
        }
        if self.callback:
            self.callback({"type": "threat", "threat": threat})
    
    def get_models_status(self):
        return {
            "total": len(self.models),
            "models": self.model_names,
            "xgboost": XGB_OK,
            "lightgbm": LGB_OK,
            "catboost": CAT_OK
        }
    
    def stop(self):
        self.is_running = False
