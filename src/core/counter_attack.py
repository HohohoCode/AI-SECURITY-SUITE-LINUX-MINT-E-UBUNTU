import time
import subprocess

class CounterAttack:
    def __init__(self, settings, callback=None):
        self.settings = settings
        self.callback = callback
        self.history = []
        
    def add_attack_record(self, ip, threat_type, info):
        record = {
            "ip": ip,
            "threat": threat_type,
            "info": info,
            "timestamp": time.time()
        }
        self.history.insert(0, record)
        if self.callback:
            self.callback({
                "type": "counter_attack",
                "ip": ip,
                "threat": threat_type,
                "info": info,
                "timestamp": time.time()
            })
    
    def get_history(self):
        return self.history
