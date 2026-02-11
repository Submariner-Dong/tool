# 配置文件
import json
import os

class Settings:
    def __init__(self):
        self.config_file = "config.json"
        self.default_config = {
            "max_count": 20,
            "proxy_enabled": False,
            "proxy_url": "",
            "window_count": 2,
            "browser_width": 550,
            "browser_height": 650,
            "fail_threshold": 10,
            "skip_threshold": 10,
            "headless_mode": True
        }
        self.load_config()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = self.default_config.copy()
            self.save_config()
    
    def save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def set(self, key, value):
        self.config[key] = value
        self.save_config()

# 全局设置实例
settings = Settings()