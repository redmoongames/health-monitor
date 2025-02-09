import json
import psutil

class HealthMonitor:
    def __init__(self):
        self.cpu_percent = 0
        self.every_cpu_core_percent = []
        self.total_cores = 0
        self.ram_percent = 0
        self.ssd_usage = 0

    def update(self):
        self.cpu_percent = psutil.cpu_percent()
        self.every_cpu_core_percent = psutil.cpu_percent(percpu=True)
        self.total_cores = len(self.every_cpu_core_percent)
        self.ram_percent = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/')
        self.ssd_usage = disk_usage.percent

    def get_top_processes_by_memory(self, num_processes=5):
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cmdline']):
            try:
                processes.append(proc.info)
            except psutil.NoSuchProcess:
                pass
        processes.sort(key=lambda proc: proc['memory_percent'], reverse=True)
        return processes[:num_processes]
    