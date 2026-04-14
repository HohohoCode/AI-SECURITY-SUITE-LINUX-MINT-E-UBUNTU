import json
from pathlib import Path

class Settings:
    CONFIG_DIR = Path.home() / ".ai-security-suite"
    CONFIG_FILE = CONFIG_DIR / "settings.json"
    DEFAULT = {"auto_block": True, "auto_counter": True, "sensitivity": 70}
    
    def __init__(self):
        self.settings = self.DEFAULT.copy()
        self.load()
    
    def load(self):
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE) as f:
                    self.settings.update(json.load(f))
            except: pass
    
    def save(self):
        self.CONFIG_DIR.mkdir(exist_ok=True)
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(self.settings, f)
    
    def get(self, key, default=None): return self.settings.get(key, default)
    def set(self, key, value): self.settings[key] = value; self.save()
