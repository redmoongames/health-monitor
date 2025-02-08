from django.http import JsonResponse
from .models import HealthStat

def health_stat_view(request):
    # Get the latest health stat entry
    try:
        stat = HealthStat.objects.latest('timestamp')
        data = {
            'cpu_percent': stat.cpu_percent,
            'total_cores': stat.total_cores,
            'every_cpu_core_percent': stat.every_cpu_core_percent,
            'ram_percent': stat.ram_percent,
            'ssd_usage': stat.ssd_usage,
        }
    except HealthStat.DoesNotExist:
        # Handle the case where no data is available
        data = {
            'error': 'No health statistics available.'
        }
    return JsonResponse(data)
