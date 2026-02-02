from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtCharts import *
import sys


class LinearChart(QWidget):
    def __init__(self, title="Linear Chart", parent=None):
        super().__init__(parent)

        # Serie
        self.series = QLineSeries()

        # Chart
        self.chart = QChart()
        self.chart.legend().hide()
        self.chart.addSeries(self.series)
        self.chart.createDefaultAxes()
        self.chart.setTitle(title)

        self.chart.setMargins(QMargins(0, 0, 0, 0))
        self.chart.setBackgroundRoundness(0)
        self.chart.setBackgroundVisible(False)

        # Ocultar ejes
        self.chart.axes(Qt.Horizontal)[0].setVisible(False)
        self.chart.axes(Qt.Vertical)[0].setVisible(False)

        # Chart view (esto ES el widget visual)
        self.view = QChartView(self.chart)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setContentsMargins(0, 0, 0, 0)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)

    def add_data_point(self, x, y):
        self.series.append(x, y)
