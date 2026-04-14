import random

class IPGenerator:
    """Gera IPs externos para testes"""
    
    # IPs de países comuns em ataques
    EXTERNAL_IPS = [
        "185.130.5.253",   # Rússia
        "185.220.101.1",   # Alemanha
        "45.227.254.1",    # Brasil
        "103.115.16.1",    # China
        "5.188.86.1",      # Holanda
        "185.165.29.1",    # Ucrânia
        "94.102.61.1",     # Romênia
        "185.244.36.1",    # Suécia
        "45.155.205.1",    # França
        "185.174.137.1"    # Polônia
    ]
    
    @staticmethod
    def get_random_external_ip():
        """Retorna um IP externo aleatório"""
        return random.choice(IPGenerator.EXTERNAL_IPS)
    
    @staticmethod
    def is_external_ip(ip):
        """Verifica se é um IP externo (não local)"""
        private_prefixes = ['10.', '192.168.', '172.16.', '172.17.', '172.18.', 
                           '172.19.', '172.20.', '172.21.', '172.22.', '172.23.',
                           '172.24.', '172.25.', '172.26.', '172.27.', '172.28.',
                           '172.29.', '172.30.', '172.31.', '127.', '0.']
        for prefix in private_prefixes:
            if ip.startswith(prefix):
                return False
        return True
