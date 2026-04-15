import subprocess
import re

class FirewallUtils:
    @staticmethod
    def get_status():
        """Retorna o status real do firewall"""
        try:
            result = subprocess.run("sudo ufw status", shell=True, capture_output=True, text=True, timeout=5)
            output = result.stdout.lower()
            # Verificar em português ou inglês
            if "status: active" in output or "estado: ativo" in output or "active" in output:
                return True
            return False
        except Exception as e:
            print(f"Erro ao verificar firewall: {e}")
            return False
    
    @staticmethod
    def enable():
        try:
            subprocess.run("sudo ufw --force enable", shell=True, timeout=10)
            subprocess.run("sudo ufw default deny incoming", shell=True, timeout=10)
            subprocess.run("sudo ufw default allow outgoing", shell=True, timeout=10)
            return True
        except:
            return False
    
    @staticmethod
    def disable():
        try:
            subprocess.run("sudo ufw disable", shell=True, timeout=10)
            return True
        except:
            return False
    
    @staticmethod
    def get_rules():
        try:
            result = subprocess.run("sudo ufw status numbered", shell=True, capture_output=True, text=True, timeout=5)
            return result.stdout if result.stdout else "Nenhuma regra"
        except:
            return "Erro"
    
    @staticmethod
    def get_blocked_ips():
        try:
            result = subprocess.run("sudo ufw status | grep DENY", shell=True, capture_output=True, text=True, timeout=5)
            return re.findall(r'\d+\.\d+\.\d+\.\d+', result.stdout)
        except:
            return []
    
    @staticmethod
    def block_ip(ip, reason):
        try:
            subprocess.run(f"sudo ufw deny from {ip} comment '{reason}'", shell=True, timeout=10)
            return True
        except:
            return False
    
    @staticmethod
    def unblock_ip(ip):
        try:
            subprocess.run(f"sudo ufw delete deny from {ip}", shell=True, capture_output=True, timeout=10)
            return True
        except:
            return False
    
    @staticmethod
    def reset():
        try:
            subprocess.run("sudo ufw --force disable", shell=True, timeout=10)
            subprocess.run("sudo ufw --force reset", shell=True, timeout=10)
            subprocess.run("sudo ufw default deny incoming", shell=True, timeout=10)
            subprocess.run("sudo ufw default allow outgoing", shell=True, timeout=10)
            subprocess.run("sudo ufw allow 22/tcp", shell=True, timeout=10)
            subprocess.run("sudo ufw allow 80/tcp", shell=True, timeout=10)
            subprocess.run("sudo ufw allow 443/tcp", shell=True, timeout=10)
            subprocess.run("sudo ufw --force enable", shell=True, timeout=10)
            return True
        except:
            return False
