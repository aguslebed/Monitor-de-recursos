from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtCharts import *
import sys

class SystemMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(800,600)
        self.setStyleSheet("background-color: #646464;")
        self.setWindowTitle("Monitor de recursos del sistema y procesos")

        self.menuFrame = QFrame(self)
        self.menuFrame.setGeometry(0, 0, 150, 600)
        self.menuFrame.setStyleSheet("background-color: #4A4A4A;")

        self.resourceButton = QPushButton("Recursos", self.menuFrame)
        self.resourceButton.setGeometry(0, 10, 150, 50)
        self.resourceButton.setStyleSheet("background-color: #5A5A5A;")

        self.processButton = QPushButton("Procesos", self.menuFrame)
        self.processButton.setGeometry(0, 70, 150, 50)
        self.processButton.setStyleSheet("background-color: #5A5A5A;")

        self.componentButton = QPushButton("Componentes", self.menuFrame)
        self.componentButton.setGeometry(0, 130, 150, 50)
        self.componentButton.setStyleSheet("background-color: #5A5A5A;")

        self.temperatureButton = QPushButton("Temperaturas", self.menuFrame)
        self.temperatureButton.setGeometry(0, 190, 150, 50)
        self.temperatureButton.setStyleSheet("background-color: #5A5A5A;")

        self.contentFrame = QFrame(self)
        self.contentFrame.setGeometry(150, 0, 650, 600)
        self.contentFrame.setStyleSheet("background-color: #7A7A7A;")

        self.series = QLineSeries()
        self.series.append(0, 6)
        self.series.append(2, 4)
        self.series.append(3, 8)
        self.series.append(7, 4)
        self.series.append(10, 5)

        self.chart = QChart()
        self.chart.legend().hide()
        self.chart.addSeries(self.series)
        self.chart.createDefaultAxes()
        self.chart.setTitle("Uso CPU (%)")
        self.chart.setMargins(QMargins(0, 0, 0, 0))
        self.chart.setBackgroundRoundness(0)
        self.chart.setBackgroundVisible(False)
        self.chart.setBackgroundBrush(QBrush(QColor("#7A7A7A")))
        self.chart.axes(Qt.Horizontal)[0].setVisible(False)
        self.chart.axes(Qt.Vertical)[0].setVisible(False)



        self._chart_view = QChartView(self.chart, self.contentFrame)
        self._chart_view.setContentsMargins(0, 0, 0, 0)
        self._chart_view.setGeometry(25, 25, 600, 100)
        self._chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)


app = QApplication(sys.argv)
window = SystemMonitor()
window.show()
sys.exit(app.exec())