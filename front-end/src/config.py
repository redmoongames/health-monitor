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