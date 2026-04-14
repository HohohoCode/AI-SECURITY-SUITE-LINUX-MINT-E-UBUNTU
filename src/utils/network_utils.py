import subprocess
import socket
import urllib.request
import json

class NetworkUtils:
    @staticmethod
    def get_whois(ip):
        try:
            result = subprocess.run(f"whois {ip} 2>/dev/null | head -10", shell=True, capture_output=True, text=True, timeout=10)
            return result.stdout[:300] if result.stdout else "N/A"
        except:
            return "N/A"
    
    @staticmethod
    def get_geolocation(ip):
        try:
            url = f"http://ip-api.com/json/{ip}"
            response = urllib.request.urlopen(url, timeout=5)
            data = json.loads(response.read().decode())
            if data.get('status') == 'success':
                return f"{data.get('city', 'N/A')}, {data.get('country', 'N/A')}"
            return "N/A"
        except:
            return "N/A"
