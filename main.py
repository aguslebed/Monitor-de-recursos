from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtCharts import *
import sys
from linearChart import LinearChart

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

        cpu_chart = LinearChart("CPU Usage")
        cpu_chart.add_data_point(0, 30)
        cpu_chart.add_data_point(1, 50)
        cpu_chart.add_data_point(2, 40)
        cpu_chart.add_data_point(3, 70)
        cpu_chart.add_data_point(4, 60)     
        

        layout = QVBoxLayout(self.contentFrame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(cpu_chart)



app = QApplication(sys.argv)
window = SystemMonitor()
window.show()
sys.exit(app.exec())