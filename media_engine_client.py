import requests
from typing import Optional, Dict, Any

class MediaEngineClient:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
    
    def get_current_track(self) -> Optional[Dict[str, Any]]:
        """Получить информацию о текущем треке"""
        try:
            response = requests.get(f"{self.base_url}/api/track", timeout=2)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting track: {e}")
            return None
    
    def set_delay(self, delay_ms: int) -> bool:
        """Установить задержку в миллисекундах"""
        try:
            response = requests.post(
                f"{self.base_url}/api/delay",
                params={"delayMs": delay_ms},
                timeout=2
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error setting delay: {e}")
            return False
    
    def get_status(self) -> Optional[Dict[str, Any]]:
        """Получить статус сервиса"""
        try:
            response = requests.get(f"{self.base_url}/api/status", timeout=2)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting status: {e}")
            return None
