import sys
from PyQt6.QtWidgets import QApplication

from src.resource_monitor import ResourceMonitor

if __name__ == '__main__':
    app = QApplication(sys.argv)
    monitor = ResourceMonitor()
    monitor.show()
    sys.exit(app.exec())