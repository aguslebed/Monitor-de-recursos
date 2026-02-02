from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtCore import Qt, QMargins
from PySide6.QtGui import QPainter, QPen, QColor


class LinearChart(QWidget):
    def __init__(self, title="Linear Chart", parent=None):
        super().__init__(parent)

        # Serie
        self.series = QLineSeries()
        pen = QPen(QColor("#00FFFF"))
        pen.setWidth(3)
        self.series.setPen(pen)

        # Chart
        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.setTitle(title)
        self.chart.legend().hide()
        # Fondo transparente
        self.chart.setBackgroundVisible(False)

        # Ejes Explicitos
        self.axisX = QValueAxis()
        self.axisY = QValueAxis()
        
        # Ocultamos la visualizacion de los ejes (lineas, etiquetas)
        self.axisX.setVisible(False)
        self.axisY.setVisible(False)

        # Agregamos los ejes al grafico
        self.chart.addAxis(self.axisX, Qt.AlignBottom)
        self.chart.addAxis(self.axisY, Qt.AlignLeft)

        # Atachamos la serie a los ejes
        self.series.attachAxis(self.axisX)
        self.series.attachAxis(self.axisY)

        # Vista
        self.view = QChartView(self.chart)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setContentsMargins(0, 0, 0, 0)
        self.view.setStyleSheet("background: transparent;") # Asegurar transparencia en la vista

        # Layout interno
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)

        # Variables para tracking de min/max
        self.min_x = float('inf')
        self.max_x = float('-inf')
        self.min_y = float('inf')
        self.max_y = float('-inf')

    def add_data_point(self, x, y):
        self.series.append(x, y)
        
        # Actualizar rangos
        if x < self.min_x: self.min_x = x
        if x > self.max_x: self.max_x = x
        if y < self.min_y: self.min_y = y
        if y > self.max_y: self.max_y = y

        # Aplicar rango a los ejes con un pequeño margen si se desea, 
        # o exacto. Para monitores, exacto en X y algo de margen en Y suele ser mejor.
        
        self.axisX.setRange(self.min_x, self.max_x)
        
        # Para Y, si es porcentaje CPU, idealmente 0-100, pero lo hacemos dinamico
        # para que sirva para temperaturas etc.
        # Si min y max son iguales, damos un margen default
        
        lower_y = self.min_y
        upper_y = self.max_y
        
        if lower_y == upper_y:
            lower_y -= 1
            upper_y += 1
            
        # Margen del 10%
        margin = (upper_y - lower_y) * 0.1
        self.axisY.setRange(max(0, lower_y - margin), upper_y + margin)

