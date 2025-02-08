from django.core.management.base import BaseCommand
from health_monitor.models import HealthStat
import time

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



class Command(BaseCommand):
    help = 'Runs the health monitor and saves data to the database'

    def handle(self, *args, **kwargs):
        monitor = HealthMonitor()
        while True:
            monitor.update()
            HealthStat.objects.create(
                cpu_percent=monitor.cpu_percent,
                total_cores=monitor.total_cores,
                every_cpu_core_percent=monitor.every_cpu_core_percent,
                ram_percent=monitor.ram_percent,
                ssd_usage=monitor.ssd_usage,
            )
            time.sleep(10)  # Update every 10 seconds