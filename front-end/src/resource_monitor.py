import ast
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtCore import QTimer, Qt, QRect




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


from PyQt6.QtGui import QColor
WINDOW_TITLE = "HP Monitor"
WINDOW_GEOMETRY = (100, 100, 280, 380)
BACKGROUND_COLOR = QColor(0, 0, 0, 180)
TEXT_COLOR = QColor(255, 255, 255, 128)
BAR_HEIGHTS = {
    'cpu_cores': 40,
    'total_cpu': 20,
    'ram': 20,
    'ssd': 20
}
UPDATE_TIME_IN_SECONDS = 1
RAM_TOP_RESULTS = 10


class ResourceMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.health_monitor = HealthMonitor()
        self.init_ui()
        self.start_timer()

    def init_ui(self):
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(*WINDOW_GEOMETRY)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")

        self.layout = QVBoxLayout(self)
        self.labels = {name: QLabel(self) for name in ['cpu', 'ram', 'ssd']}
        for label in self.labels.values():
            self.layout.addWidget(label)

    def start_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_values)
        self.timer.start(int(UPDATE_TIME_IN_SECONDS * 1000))

    def update_values(self):
        self.health_monitor.update()
        self.repaint()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), BACKGROUND_COLOR)
        painter.setPen(TEXT_COLOR)
        painter.setFont(QFont('SansSerif', 11))

        vertical_offset = 10
        vertical_offset = self.draw_cpu_cores_performance(painter, vertical_offset)
        vertical_offset = self.draw_total_cpu_performance(painter, vertical_offset)
        vertical_offset = self.draw_ssd_usage(painter, vertical_offset)
        vertical_offset = self.draw_ram_usage(painter, vertical_offset)
        self.draw_top_ram_processes(painter, vertical_offset, RAM_TOP_RESULTS)

    def draw_cpu_cores_performance(self, painter, offset):
        if not self.health_monitor or self.health_monitor.total_cores <= 0:
            return offset
        
        chart_width = self.width()
        rect_width = int(chart_width / self.health_monitor.total_cores)
        for i, core_usage in enumerate(self.health_monitor.every_cpu_core_percent):
            x = i * rect_width
            y = offset + BAR_HEIGHTS['cpu_cores'] - int(core_usage / 100 * BAR_HEIGHTS['cpu_cores'])
            rect_height = int(core_usage / 100 * BAR_HEIGHTS['cpu_cores'])
            painter.fillRect(x, y, rect_width, rect_height, QColor(0, 128, 0, 128))
        
        return offset + BAR_HEIGHTS['cpu_cores'] + 10

    def draw_total_cpu_performance(self, painter, offset):
        text = f'CPU: {self.health_monitor.cpu_percent}%'
        color = QColor(0, 128, 0, 128)
        value = self.health_monitor.cpu_percent / 100
        return self.draw_bar(painter, offset, BAR_HEIGHTS['total_cpu'], value, color, text)

    def draw_ram_usage(self, painter, offset):
        text = f'RAM: {self.health_monitor.ram_percent:.2f}%'
        color = QColor(255, 165, 0, 128)
        value = self.health_monitor.ram_percent / 100
        return self.draw_bar(painter, offset, BAR_HEIGHTS['ram'], value, color, text)

    def draw_ssd_usage(self, painter, offset):
        text = f'SSD: {self.health_monitor.ssd_usage:.2f}%'
        color = QColor(128, 0, 128, 128)
        value = self.health_monitor.ssd_usage / 100
        return self.draw_bar(painter, offset, BAR_HEIGHTS['ssd'], value, color, text)
    
    def draw_bar(self, painter: QPainter, offset: int, height: int, value: float, color: QColor, text: str):
        value = min(max(value, 0), 1)
        fill_width = int(self.width() * value)
        painter.fillRect(QRect(10, offset, fill_width, height), color)
        painter.drawText(QRect(10, offset, self.width(), height), Qt.AlignmentFlag.AlignCenter, text)
        return offset + height + 10

    def draw_top_ram_processes(self, painter: QPainter, offset: int, num_processes: int = 5):
        top_processes = self.health_monitor.get_top_processes_by_memory(num_processes)
        offset += 15
        
        name_pid_column_x = 10
        memory_column_x = 230 

        for process in top_processes:
            process_name = f"{process['name']} #{process['pid']} "
            process_memory = f"{process['memory_percent']:.2f}%"
            painter.setPen(TEXT_COLOR)
            painter.drawText(name_pid_column_x, offset, process_name[:28])
            painter.drawText(memory_column_x, offset, process_memory)
            offset += 15
            command = self.parse_command(process['cmdline'])
            painter.drawText(name_pid_column_x, offset, command)
            offset += 30
        return offset + 10

    def parse_command(self, cmdline):
        try:
            actual_list = ast.literal_eval(str(cmdline))
            return str(actual_list[0])
        except Exception as e:
            print(e)
            return str(cmdline)
