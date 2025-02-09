from flask import Flask, jsonify
import time
from src.health_monitor import HealthMonitor
from datetime import datetime, timedelta

app = Flask(__name__)
monitor = HealthMonitor()
last_update = None
update_interval = timedelta(seconds=0.2)

@app.route('/api/health', methods=['GET'])
def get_health():
    try:
        global last_update
        global monitor
        global update_interval

        current_time = datetime.now()

        if last_update is None or (current_time - last_update) >= update_interval:
            monitor.update()
            last_update = current_time

        health_data = {
            'status': 'success',
            'monitor': {
                'cpu_percent': monitor.cpu_percent,
                'every_cpu_core_percent': monitor.every_cpu_core_percent,
                'total_cores': monitor.total_cores,
                'ram_percent': monitor.ram_percent,
                'ssd_usage': monitor.ssd_usage
            }
        }
        return jsonify(health_data)
    except:
        health_data = {
            'status': 'fail',
            'monitor': {}
        }
        return jsonify(health_data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=11506)
