import sys
import psutil
import json
import ast
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtCore import QTimer, Qt, QRect

class Config:
    default_update_time_in_seconds = 1
    default_config_file = 'config.json'

    def __init__(self):
        self.update_time_in_seconds = self.try_load_update_time()
        
    def try_load_update_time(self) -> float:
        try:
            with open(self.default_config_file, 'r') as json_data:
                data = json.load(json_data)
                if 'update_time_in_seconds' in data:
                    return data['update_time_in_seconds']
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Error reading config.json")
        return self.default_update_time_in_seconds
    

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


class ResourceMonitor(QWidget):
    def __init__(self):
        super().__init__()
        config = Config()
        self.health_monitor = HealthMonitor()

        self.setWindowTitle('HP Monitor')
        self.setGeometry(100, 100, 280, 380)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")

        self.layout = QVBoxLayout(self)
        self.labels = {
            'cpu': QLabel(self),
            'ram': QLabel(self),
            'ssd': QLabel(self)
        }
        for label in self.labels.values():
            self.layout.addWidget(label)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_values)
        self.timer.start(int(config.update_time_in_seconds * 1000))

    def update_values(self):
        self.health_monitor.update()
        self.repaint()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        semi_transparent_brush = QColor(0, 0, 0, 128)
        painter.fillRect(self.rect(), semi_transparent_brush)

        painter.setPen(Qt.GlobalColor.white)
        painter.setFont(QFont('SansSerif', 10))

        vertical_offset = 10

        vertical_offset = self.draw_cpu_cores_performance(painter, vertical_offset, 40)
        vertical_offset = self.draw_total_cpu_performance(painter, vertical_offset, 20)
        vertical_offset = self.draw_ssd_usage(painter, vertical_offset, 20)
        vertical_offset = self.draw_ram_usage(painter, vertical_offset, 20)
        vertical_offset = self.draw_top_ram_processes(painter, vertical_offset, 10)

    def draw_cpu_cores_performance(self, painter, offset, height=40):
        if not self.health_monitor or self.health_monitor.total_cores <= 0:
            return offset
        
        chart_width = self.width()
        rect_width = int(chart_width / self.health_monitor.total_cores)

        for i, core_usage in enumerate(self.health_monitor.every_cpu_core_percent):
            x = i * rect_width
            y = offset + height - int(core_usage / 100 * height)
            width = rect_width
            rect_height = int(core_usage / 100 * height)

            painter.fillRect(x, y, width, rect_height, QColor(0, 128, 0, 128))
        return offset + height + 10

    def draw_total_cpu_performance(self, painter, offset, height=20):
        text = f'CPU: {self.health_monitor.cpu_percent}%'
        color = QColor(0, 128, 0, 128)
        value = self.health_monitor.cpu_percent / 100
        return self.draw_bar_dashboard(painter, offset, height, value, color, text)

    def draw_ram_usage(self, painter, offset, height=20):
        text = f'RAM: {self.health_monitor.ram_percent:.2f}%'
        color = QColor(255, 165, 0, 128)
        value = self.health_monitor.ram_percent / 100
        return self.draw_bar_dashboard(painter, offset, height, value, color, text)

    def draw_ssd_usage(self, painter, offset, height=20):
        text = f'SSD: {self.health_monitor.ssd_usage:.2f}%'
        color = QColor(128, 0, 128, 128)
        value = self.health_monitor.ssd_usage / 100
        return self.draw_bar_dashboard(painter, offset, height, value, color, text)
    
    def draw_bar_dashboard(self, painter: QPainter, offset: int, height: int, value: float, color: QColor, text: str):
        if value < 0:
            value = 0
        elif value > 1:
            value = 1
            
        fill_width = int(self.width() * value)
        fill_rect = QRect(10, offset, fill_width, height)
        painter.fillRect(fill_rect, color)
        text_rect = QRect(10, offset, self.width(), height)
        painter.setPen(QColor(255, 255, 255, 128))
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)
        return offset + height + 10

    def draw_top_ram_processes(self, painter: QPainter, offset: int, num_processes: int = 5):
        top_processes = self.health_monitor.get_top_processes_by_memory(num_processes)
        offset += 15
        
        name_pid_column_x = 10
        memory_column_x = 230 

        for process in top_processes:
            process_name = f"{process['name']} #{process['pid']} "
            process_memory = f"{process['memory_percent']:.2f}%"
            painter.setPen(QColor(255, 255, 255, 128))
            painter.drawText(name_pid_column_x, offset, process_name[:28])
            painter.setPen(QColor(255, 255, 255, 180))
            painter.drawText(memory_column_x, offset, process_memory)
            offset += 15
            command = ""
            try:
                actual_list = ast.literal_eval(str(process['cmdline']))
                command = str(actual_list[0])
            except Exception as e:
                print(e)
                command = str(process['cmdline'])

            painter.setPen(QColor(255, 255, 255, 128))
            painter.drawText(name_pid_column_x, offset, command)
            offset += 30
        return offset + 10

if __name__ == '__main__':
    app = QApplication(sys.argv)
    monitor = ResourceMonitor()
    monitor.show()
    sys.exit(app.exec())
