from pythonosc import udp_client
from typing import Optional

class VRChatChatbox:
    def __init__(self, ip: str = "127.0.0.1", port: int = 9000):
        self.client = udp_client.SimpleUDPClient(ip, port)
    
    def send_message(self, message: str) -> bool:
        """Отправить сообщение в VRChat chatbox через OSC"""
        try:
            self.client.send_message("/chatbox/input", [message, True])
            return True
        except Exception as e:
            print(f"Error sending to VRChat: {e}")
            return False
    
    def format_track_message(self, track_info: dict, config=None) -> str:
        """Форматировать информацию о треке для VRChat"""
        title = track_info.get('title', 'none')
        artist = track_info.get('artist', '')
        is_paused = track_info.get('isPaused', False)
        
        if title == 'none':
            return "🎵 No track playing"
        
        # Получаем иконки из конфига
        if config:
            playing_icon = config.get('playing_icon', '▶')
            paused_icon = config.get('paused_icon', '⏸')
            show_icon = config.get('show_status_icon', True)
            format_type = config.get('format', 'display')
        else:
            playing_icon = '▶'
            paused_icon = '⏸'
            show_icon = True
            format_type = 'display'
        
        status = paused_icon if is_paused else playing_icon
        
        # Форматируем сообщение в зависимости от выбранного формата
        if format_type == 'display':
            message = track_info.get('display', f"{artist} - {title}")
        elif format_type == 'artist_track':
            message = f"{artist} - {title}"
        elif format_type == 'track_artist':
            message = f"{title} - {artist}"
        elif format_type == 'track_by_artist':
            message = f"{title} by {artist}"
        elif format_type == 'track_only':
            message = title
        else:
            message = track_info.get('display', f"{artist} - {title}")
        
        if show_icon:
            return f"{status} {message}"
        else:
            return message
