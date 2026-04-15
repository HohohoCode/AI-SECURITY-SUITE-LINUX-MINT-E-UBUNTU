"""
THREAT INTELLIGENCE - Inteligência de Ameaças
- Feeds de IPs maliciosos
- Listas negras atualizadas
- Reputação de IPs
"""

import subprocess
import re
import threading
import time
import urllib.request
import json
from datetime import datetime

class ThreatIntelligence:
    """Sistema de inteligência de ameaças"""
    
    # Feeds públicos de IPs maliciosos
    BLACKLIST_FEEDS = [
        "https://raw.githubusercontent.com/firehol/blocklist-ipsets/master/firehol_level1.netset",
        "https://raw.githubusercontent.com/firehol/blocklist-ipsets/master/stopforumspam.ipset",
        "https://rules.emergingthreats.net/fwrules/emerging-Block-IPs.txt"
    ]
    
    def __init__(self, callback=None):
        self.callback = callback
        self.malicious_ips = set()
        self.ip_reputation = {}
        self.last_update = None
        self.is_updating = False
        
    def start(self):
        """Inicia o serviço de inteligência"""
        self._log("🕵️ Threat Intelligence ativado", "success")
        self.update_blacklists()
        self.start_auto_update()
    
    def update_blacklists(self):
        """Atualiza listas negras de IPs maliciosos"""
        if self.is_updating:
            return
        
        def update():
            self.is_updating = True
            self._log("Atualizando listas negras...", "info")
            
            new_ips = set()
            
            for feed_url in self.BLACKLIST_FEEDS:
                try:
                    response = urllib.request.urlopen(feed_url, timeout=30)
                    content = response.read().decode('utf-8')
                    
                    # Extrair IPs do conteúdo
                    ips = re.findall(r'(\d+\.\d+\.\d+\.\d+/\d+|\d+\.\d+\.\d+\.\d+)', content)
                    for ip in ips:
                        if '/' in ip:
                            # Expandir CIDR (simplificado)
                            new_ips.add(ip.split('/')[0])
                        else:
                            new_ips.add(ip)
                            
                    self._log(f"   {len(ips)} IPs carregados de {feed_url.split('/')[-1]}", "info")
                except Exception as e:
                    self._log(f"   Erro ao carregar {feed_url}: {e}", "error")
            
            self.malicious_ips = new_ips
            self.last_update = datetime.now()
            self._log(f"✅ Lista atualizada: {len(self.malicious_ips)} IPs maliciosos", "success")
            self.is_updating = False
        
        threading.Thread(target=update, daemon=True).start()
    
    def start_auto_update(self):
        """Atualização automática a cada 6 horas"""
        def update_loop():
            while True:
                time.sleep(21600)  # 6 horas
                self.update_blacklists()
        threading.Thread(target=update_loop, daemon=True).start()
    
    def check_ip(self, ip):
        """Verifica se um IP é malicioso"""
        # Verificar em listas negras locais
        if ip in self.malicious_ips:
            return True, "Lista negra pública"
        
        # Verificar reputação online
        reputation = self._check_reputation_online(ip)
        if reputation:
            return True, f"Reputação: {reputation}"
        
        # Verificar em logs locais
        if self._check_local_logs(ip):
            return True, "Histórico de ataques local"
        
        return False, "IP limpo"
    
    def _check_reputation_online(self, ip):
        """Verifica reputação online via API"""
        try:
            url = f"http://ip-api.com/json/{ip}"
            response = urllib.request.urlopen(url, timeout=5)
            data = json.loads(response.read().decode())
            
            # Países de alto risco
            high_risk = ['RU', 'CN', 'KP', 'IR', 'SY', 'UA']
            if data.get('countryCode') in high_risk:
                return "País de alto risco"
            
            # ISPs conhecidos por ataques
            bad_isps = ['DigitalOcean', 'Vultr', 'Linode', 'AWS', 'OVH']
            isp = data.get('isp', '')
            for bad_isp in bad_isps:
                if bad_isp.lower() in isp.lower():
                    return f"ISP suspeito: {isp}"
                    
        except:
            pass
        return None
    
    def _check_local_logs(self, ip):
        """Verifica em logs locais se o IP já atacou antes"""
        try:
            # Verificar em logs de autenticação
            result = subprocess.run(f"sudo grep '{ip}' /var/log/auth.log 2>/dev/null | wc -l",
                                   shell=True, capture_output=True, text=True, timeout=5)
            if int(result.stdout.strip()) > 5:
                return True
        except:
            pass
        return False
    
    def get_blocked_stats(self):
        """Retorna estatísticas das listas negras"""
        return {
            "total_malicious_ips": len(self.malicious_ips),
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "is_updating": self.is_updating
        }
    
    def _log(self, msg, level="info"):
        if self.callback:
            self.callback({"type": "log", "message": f"[THREAT-INTEL] {msg}", "level": level})
        print(f"[THREAT-INTEL] {msg}")
