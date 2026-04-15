"""
HONEYPOT - Sistema de Pote de Mel
- Portas falsas para atrair atacantes
- Registro de técnicas de ataque
- Desvio de atenção
"""

import socket
import threading
import time
import subprocess
import re
from datetime import datetime

class Honeypot:
    """Sistema de honeypot para atrair e registrar atacantes"""
    
    def __init__(self, callback=None):
        self.callback = callback
        self.is_running = False
        self.attacks_log = []
        self.fake_services = {
            21: "FTP Service",      # FTP falso
            22: "SSH Service",      # SSH falso
            23: "Telnet Service",   # Telnet falso
            80: "Web Server",       # HTTP falso
            443: "HTTPS Server",    # HTTPS falso
            3306: "MySQL Database", # MySQL falso
            3389: "RDP Service",    # RDP falso
            8080: "Proxy Server",   # Proxy falso
            5900: "VNC Server",     # VNC falso
            25: "SMTP Server",      # Email falso
        }
        self.active_sockets = []
        
    def start(self):
        """Inicia o honeypot"""
        self.is_running = True
        self._log("🍯 Honeypot ativado - Atraindo atacantes...", "success")
        
        for port, service in self.fake_services.items():
            thread = threading.Thread(target=self._run_fake_service, args=(port, service), daemon=True)
            thread.start()
            self._log(f"   Porta {port} ({service}) - Escutando", "info")
    
    def stop(self):
        """Para o honeypot"""
        self.is_running = False
        for sock in self.active_sockets:
            try:
                sock.close()
            except:
                pass
        self._log("🍯 Honeypot desativado", "warning")
    
    def _run_fake_service(self, port, service_name):
        """Executa um serviço falso na porta especificada"""
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(('0.0.0.0', port))
            server.listen(5)
            server.settimeout(1)
            self.active_sockets.append(server)
            
            while self.is_running:
                try:
                    client, addr = server.accept()
                    client_ip = addr[0]
                    
                    # Registrar tentativa de conexão
                    self._log_attack(client_ip, port, service_name)
                    
                    # Enviar banner falso
                    banner = self._get_fake_banner(port, service_name)
                    client.send(banner.encode())
                    
                    # Ler dados do atacante (se houver)
                    try:
                        data = client.recv(1024)
                        if data:
                            self._analyze_attack_data(client_ip, port, data)
                    except:
                        pass
                    
                    client.close()
                except socket.timeout:
                    continue
                except Exception as e:
                    pass
        except Exception as e:
            pass
    
    def _get_fake_banner(self, port, service_name):
        """Retorna banner falso para o serviço"""
        banners = {
            21: "220 (vsFTPd 3.0.3)\r\n",
            22: "SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.6\r\n",
            23: "\r\nWelcome to Telnet Server\r\nlogin: ",
            80: "HTTP/1.1 200 OK\r\nServer: Apache/2.4.52\r\n\r\n<html><body><h1>Welcome</h1></body></html>",
            443: "HTTP/1.1 200 OK\r\nServer: nginx/1.18.0\r\n",
            3306: "5.7.38-0ubuntu0.18.04.1\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
            3389: "\x03\x00\x00\x0b\x06\xd0\x00\x00\x12\x34\x56\x78",
            8080: "HTTP/1.1 200 OK\r\nServer: Tomcat\r\n\r\n",
            5900: "RFB 003.008\n",
            25: "220 mail.example.com ESMTP Postfix\r\n"
        }
        return banners.get(port, f"220 {service_name} Ready\r\n")
    
    def _log_attack(self, ip, port, service):
        """Registra tentativa de ataque"""
        attack = {
            "timestamp": datetime.now().isoformat(),
            "ip": ip,
            "port": port,
            "service": service,
            "type": "HONEYPOT_SCAN"
        }
        self.attacks_log.append(attack)
        self._log(f"🍯 ATACANTE DETECTADO: {ip} tentou acessar porta {port} ({service})", "alert")
        
        if self.callback:
            self.callback({
                "type": "honeypot_attack",
                "ip": ip,
                "port": port,
                "service": service,
                "timestamp": time.time()
            })
    
    def _analyze_attack_data(self, ip, port, data):
        """Analisa dados enviados pelo atacante"""
        data_str = data.decode('utf-8', errors='ignore').lower()
        
        # Detectar tipos de ataque
        if "admin" in data_str or "root" in data_str or "password" in data_str:
            self._log(f"🍯 Atacante {ip} tentou credenciais na porta {port}", "warning")
        
        if "union select" in data_str or "or 1=1" in data_str:
            self._log(f"🍯 Atacante {ip} tentou SQL Injection na porta {port}", "critical")
        
        if "<script" in data_str or "javascript:" in data_str:
            self._log(f"🍯 Atacante {ip} tentou XSS na porta {port}", "critical")
    
    def get_attacks(self):
        """Retorna lista de ataques registrados"""
        return self.attacks_log
    
    def get_stats(self):
        """Retorna estatísticas do honeypot"""
        unique_ips = set(a['ip'] for a in self.attacks_log)
        return {
            "total_attacks": len(self.attacks_log),
            "unique_attackers": len(unique_ips),
            "most_attacked_ports": self._get_most_attacked_ports(),
            "last_attack": self.attacks_log[-1] if self.attacks_log else None
        }
    
    def _get_most_attacked_ports(self):
        """Retorna portas mais atacadas"""
        from collections import Counter
        ports = [a['port'] for a in self.attacks_log]
        return Counter(ports).most_common(5)
    
    def _log(self, msg, level="info"):
        if self.callback:
            self.callback({"type": "log", "message": f"[HONEYPOT] {msg}", "level": level})
        print(f"[HONEYPOT] {msg}")
