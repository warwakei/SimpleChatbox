import json
from pathlib import Path
from typing import Dict, Any

class Config:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.defaults = {
            "format": "display",  # display, artist_track, track_artist, track_by_artist, track_only
            "show_status_icon": True,
            "playing_icon": "▶",
            "paused_icon": "⏸",
            "media_engine_url": "http://localhost:5000",
            "vrchat_ip": "127.0.0.1",
            "vrchat_port": 9000,
            "auto_send_delay": 3000
        }
        self.data = self.load()
    
    def load(self) -> Dict[str, Any]:
        """Загрузить конфиг из файла или создать новый"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.defaults.copy()
        return self.defaults.copy()
    
    def save(self):
        """Сохранить конфиг в файл"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default=None):
        """Получить значение из конфига"""
        return self.data.get(key, default if default is not None else self.defaults.get(key))
    
    def set(self, key: str, value: Any):
        """Установить значение в конфиге"""
        self.data[key] = value
        self.save()
