import psutil
from typing import Dict, Any
import threading

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

class SystemInfo:
    def __init__(self):
        self._cache = {
            "cpu": {"usage": 0, "cores": 0},
            "memory": {"used": 0, "total": 0, "percent": 0},
            "cpu_temp": 0,
            "gpu_temp": 0
        }
        self._lock = threading.Lock()
        self._wmi = None
        if WMI_AVAILABLE:
            try:
                self._wmi = wmi.WMI(namespace="root\\cimv2")
            except Exception as e:
                print(f"[SystemInfo] WMI initialization failed: {e}")
        
        self._update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self._update_thread.start()
    
    def _update_loop(self):
        """Обновлять информацию в фоне"""
        while True:
            try:
                with self._lock:
                    self._cache["cpu"]["usage"] = psutil.cpu_percent(interval=0.5)
                    self._cache["cpu"]["cores"] = psutil.cpu_count()
                    
                    memory = psutil.virtual_memory()
                    self._cache["memory"]["used"] = memory.used // (1024 ** 3)
                    self._cache["memory"]["total"] = memory.total // (1024 ** 3)
                    self._cache["memory"]["percent"] = memory.percent
                    
                    self._cache["cpu_temp"] = self._get_cpu_temp()
                    self._cache["gpu_temp"] = self._get_gpu_temp()
            except Exception as e:
                print(f"[SystemInfo] Error in update loop: {e}")
            
            threading.Event().wait(2)  # Обновлять каждые 2 секунды
    
    def _get_cpu_temp(self) -> float:
        """Получить температуру CPU через WMI"""
        try:
            if not self._wmi:
                return 0
            
            # Пытаемся получить температуру через WMI
            temps = self._wmi.query("SELECT * FROM Win32_TemperatureProbe")
            if temps:
                for temp in temps:
                    if temp.CurrentReading:
                        # WMI возвращает температуру в десятых долях Кельвина
                        kelvin = temp.CurrentReading / 10.0
                        celsius = kelvin - 273.15
                        if 0 < celsius < 150:  # Разумный диапазон
                            return celsius
            return 0
        except Exception as e:
            return 0
    
    def _get_gpu_temp(self) -> float:
        """Получить температуру GPU через WMI"""
        try:
            if not self._wmi:
                return 0
            
            # Пытаемся получить температуру GPU
            temps = self._wmi.query("SELECT * FROM Win32_VideoController")
            if temps:
                for gpu in temps:
                    if hasattr(gpu, 'CurrentTemperature') and gpu.CurrentTemperature:
                        kelvin = gpu.CurrentTemperature / 10.0
                        celsius = kelvin - 273.15
                        if 0 < celsius < 150:
                            return celsius
            return 0
        except Exception as e:
            return 0
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """Получить информацию о CPU"""
        with self._lock:
            return self._cache["cpu"].copy()
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Получить информацию о памяти"""
        with self._lock:
            return self._cache["memory"].copy()
    
    def get_gpu_temp(self) -> float:
        """Получить температуру GPU"""
        with self._lock:
            return self._cache["gpu_temp"]
    
    def get_cpu_temp(self) -> float:
        """Получить температуру CPU"""
        with self._lock:
            return self._cache["cpu_temp"]
    
    def get_all_info(self) -> Dict[str, Any]:
        """Получить всю системную информацию"""
        with self._lock:
            return {
                "cpu": self._cache["cpu"].copy(),
                "memory": self._cache["memory"].copy(),
                "cpu_temp": self._cache["cpu_temp"],
                "gpu_temp": self._cache["gpu_temp"]
            }
    
    def format_sys_message(self, config=None) -> str:
        """Форматировать системную информацию для VRChat"""
        info = self.get_all_info()
        
        parts = []
        
        # CPU Usage
        if config and config.get('show_cpu_usage', True):
            cpu_usage = info["cpu"]["usage"]
            parts.append(f"CPU: {cpu_usage:.1f}%")
        
        # RAM Usage
        if config and config.get('show_ram_usage', True):
            mem_used = info["memory"]["used"]
            mem_total = info["memory"]["total"]
            mem_percent = info["memory"]["percent"]
            parts.append(f"RAM: {mem_used}GB/{mem_total}GB ({mem_percent:.1f}%)")
        
        # CPU Temp
        if config and config.get('show_cpu_temp', True):
            cpu_temp = info["cpu_temp"]
            if cpu_temp > 0:
                parts.append(f"CPU: {cpu_temp:.1f}°C")
        
        # GPU Temp
        if config and config.get('show_gpu_temp', True):
            gpu_temp = info["gpu_temp"]
            if gpu_temp > 0:
                parts.append(f"GPU: {gpu_temp:.1f}°C")
        
        if not parts:
            return "💻 No system info"
        
        return "💻 " + " | ".join(parts)
