from django.urls import path
from .views import health_stat_view

urlpatterns = [
    path('api/health/', health_stat_view, name='health_stat'),
]
