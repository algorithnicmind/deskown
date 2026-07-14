import time
import threading

import psutil
from PyQt6.QtCore import QObject, pyqtSignal

import config


class SystemMonitor(QObject):
    stats_updated = pyqtSignal(dict)

    def __init__(self, interval: float = None):
        super().__init__()
        self.interval = interval or config.MONITOR_INTERVAL
        self._stats = {}
        self._running = False
        self._thread = None
        self._last_net = psutil.net_io_counters()
        self._last_time = time.time()

    def update(self):
        now = time.time()
        dt = now - self._last_time
        self._last_time = now

        net = psutil.net_io_counters()
        speed_up = (net.bytes_sent - self._last_net.bytes_sent) / dt if dt > 0 else 0
        speed_down = (net.bytes_recv - self._last_net.bytes_recv) / dt if dt > 0 else 0
        self._last_net = net

        self._stats = {
            "cpu": self.get_cpu(),
            "memory": self.get_memory(),
            "disk": self.get_disk(),
            "battery": self.get_battery(),
            "network": {
                "bytes_sent": net.bytes_sent,
                "bytes_recv": net.bytes_recv,
                "speed_up": speed_up,
                "speed_down": speed_down,
            },
            "processes": self.get_processes(),
        }
        self.stats_updated.emit(self._stats)

    def get_cpu(self) -> dict:
        return {
            "percent": psutil.cpu_percent(interval=0.1),
            "per_core": psutil.cpu_percent(interval=0.1, percpu=True),
            "count": psutil.cpu_count(),
        }

    def get_memory(self) -> dict:
        mem = psutil.virtual_memory()
        return {
            "percent": mem.percent,
            "used_gb": round(mem.used / (1024**3), 1),
            "total_gb": round(mem.total / (1024**3), 1),
            "available_gb": round(mem.available / (1024**3), 1),
        }

    def get_disk(self, drive: str = "C:") -> dict:
        try:
            disk = psutil.disk_usage(f"{drive}\\")
            return {
                "percent": disk.percent,
                "used_gb": round(disk.used / (1024**3), 1),
                "total_gb": round(disk.total / (1024**3), 1),
                "free_gb": round(disk.free / (1024**3), 1),
            }
        except Exception:
            return {"percent": 0, "used_gb": 0, "total_gb": 0, "free_gb": 0}

    def get_battery(self) -> dict:
        bat = psutil.sensors_battery()
        if bat is None:
            return {"percent": 0, "power_plugged": False, "seconds_left": None}
        return {
            "percent": bat.percent,
            "power_plugged": bat.power_plugged,
            "seconds_left": bat.secsleft if bat.secsleft > 0 else None,
        }

    def get_network(self) -> dict:
        net = self._stats.get("network", {})
        return net if net else {
            "bytes_sent": 0, "bytes_recv": 0,
            "speed_up": 0, "speed_down": 0,
        }

    def get_processes(self, top_n: int = 5) -> list[dict]:
        procs = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"]):
            try:
                info = p.info
                procs.append({
                    "pid": info["pid"],
                    "name": info["name"],
                    "cpu": info["cpu_percent"] or 0,
                    "memory": round((info["memory_info"].rss / (1024**2)), 1) if info["memory_info"] else 0,
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        procs.sort(key=lambda x: x["cpu"], reverse=True)
        return procs[:top_n]

    def get_all(self) -> dict:
        if not self._stats:
            self.update()
        return self._stats

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self):
        while self._running:
            self.update()
            time.sleep(self.interval)

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None
