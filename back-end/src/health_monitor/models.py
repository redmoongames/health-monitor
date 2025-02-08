from django.db import models

class HealthStat(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    cpu_percent = models.FloatField()
    total_cores = models.IntegerField()
    every_cpu_core_percent = models.JSONField()
    ram_percent = models.FloatField()
    ssd_usage = models.FloatField()

    def __str__(self):
        return f"HealthStat at {self.timestamp}"