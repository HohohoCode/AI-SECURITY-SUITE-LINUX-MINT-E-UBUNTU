import subprocess
import re

class FirewallUtils:
    @staticmethod
    def get_status():
        """Retorna o status do firewall (funciona no Ubuntu e Linux Mint)"""
        try:
            # Tentar ufw status
            result = subprocess.run("sudo ufw status", shell=True, capture_output=True, text=True, timeout=5)
            output = result.stdout.lower()
            
            # Verificar em português ou inglês
            if "status: active" in output or "estado: ativo" in output or "active" in output:
                return True
            
            # Verificar se iptables tem regras
            result = subprocess.run("sudo iptables -L -n | grep -c 'DROP\\|REJECT'", 
                                   shell=True, capture_output=True, text=True, timeout=5)
            if int(result.stdout.strip()) > 0:
                return True
                
            return False
        except Exception as e:
            print(f"Erro ao verificar firewall: {e}")
            return False
    
    @staticmethod
    def enable():
        """Ativa o firewall"""
        try:
            subprocess.run("sudo ufw --force enable", shell=True, capture_output=True, text=True, timeout=10)
            return True
        except:
            return False
    
    @staticmethod
    def disable():
        """Desativa o firewall"""
        try:
            subprocess.run("sudo ufw disable", shell=True, capture_output=True, text=True, timeout=10)
            return True
        except:
            return False
    
    @staticmethod
    def get_rules():
        """Obtém regras do firewall"""
        try:
            result = subprocess.run("sudo ufw status numbered", shell=True, capture_output=True, text=True, timeout=5)
            return result.stdout if result.stdout else "Nenhuma regra"
        except:
            return "Erro"
    
    @staticmethod
    def get_rules_list():
        """Retorna lista de regras com números"""
        rules = []
        try:
            result = subprocess.run("sudo ufw status numbered", shell=True, capture_output=True, text=True, timeout=5)
            lines = result.stdout.split('\n')
            for line in lines:
                if '[ ' in line and ']' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        num = parts[0].strip('[]')
                        rules.append({"num": num, "line": line.strip()})
            return rules
        except:
            return []
    
    @staticmethod
    def delete_rule(rule_number):
        """Remove uma regra pelo número"""
        try:
            cmd = f"echo 'y' | sudo ufw delete {rule_number}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            return result.returncode == 0, f"Regra {rule_number} removida"
        except:
            return False, "Erro ao remover regra"
    
    @staticmethod
    def delete_all_rules():
        """Remove todas as regras do firewall"""
        try:
            subprocess.run("sudo ufw --force disable", shell=True, capture_output=True, timeout=10)
            subprocess.run("sudo ufw --force reset", shell=True, capture_output=True, timeout=10)
            subprocess.run("sudo ufw --force enable", shell=True, capture_output=True, timeout=10)
            return True, "Todas as regras foram removidas"
        except:
            return False, "Erro ao limpar regras"
    
    @staticmethod
    def reset_to_default():
        """Reseta o firewall para configuração padrão"""
        try:
            subprocess.run("sudo ufw --force reset", shell=True, capture_output=True, timeout=10)
            subprocess.run("sudo ufw default deny incoming", shell=True, capture_output=True, timeout=10)
            subprocess.run("sudo ufw default allow outgoing", shell=True, capture_output=True, timeout=10)
            subprocess.run("sudo ufw --force enable", shell=True, capture_output=True, timeout=10)
            return True, "Firewall resetado para configuração padrão"
        except:
            return False, "Erro ao resetar firewall"
    
    @staticmethod
    def get_blocked_ips():
        """Obtém IPs bloqueados"""
        try:
            result = subprocess.run("sudo ufw status | grep DENY", shell=True, capture_output=True, text=True, timeout=5)
            ips = re.findall(r'\d+\.\d+\.\d+\.\d+', result.stdout)
            return list(set(ips))
        except:
            return []
    
    @staticmethod
    def delete_rule_by_ip(ip):
        """Remove todas as regras que contenham um IP específico"""
        try:
            rules = FirewallUtils.get_rules_list()
            deleted = []
            for rule in rules:
                if ip in rule['line']:
                    success, _ = FirewallUtils.delete_rule(rule['num'])
                    if success:
                        deleted.append(rule['num'])
            return len(deleted) > 0, f"{len(deleted)} regras removidas para o IP {ip}"
        except:
            return False, "Erro ao remover regras do IP"
