from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtCore import Qt, QMargins
from PySide6.QtGui import QPainter, QPen, QColor
import time

class LinearChart(QWidget):
    def __init__(self, title="Linear Chart", parent=None, y_range=None):
        super().__init__(parent)

        # Configuracion
        self.time_window = 60 # Segundos de historia visibles
        self.y_range = y_range

        # Serie
        self.series = QLineSeries()
        pen = QPen(QColor("#00FFFF"))
        pen.setWidth(2)
        self.series.setPen(pen)

        # Chart
        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.setTitle(title)
        self.chart.legend().hide()
        # Fondo transparente
        self.chart.setBackgroundVisible(False)
        
        # Color del titulo (opcional, para que contraste)
        self.chart.setTitleBrush(QColor("white"))

        # Ejes Explicitos
        self.axisX = QValueAxis()
        self.axisY = QValueAxis()
        
        self.axisX.setVisible(False)
        
        # Configuracion del Eje Y
        # Siempre visible y blanco
        self.axisY.setVisible(True)
        self.axisY.setLabelsColor(QColor("white"))

        if self.y_range:
            self.axisY.setRange(self.y_range[0], self.y_range[1])
            self.axisY.setTickCount(6) # 0, 20, 40, 60, 80, 100
        else:
            # Si es dinamico (Red), dejamos que Qt o nuestra logica maneje los ticks
            pass

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
        self.view.setStyleSheet("background: transparent;")

        # Layout interno
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)
        
        # Altura minima para que no se aplasten
        self.setMinimumHeight(200)

    def update_chart(self, value):
        """Metodo helper para actualizar solo con valor Y"""
        self.add_data_point(time.time(), value)

    def add_data_point(self, x, y):
        self.series.append(x, y)
        
        # Ventana deslizante (Scrolling)
        # El eje X va desde [ahora - ventana] hasta [ahora]
        start_time = x - self.time_window
        self.axisX.setRange(start_time, x)
        
        # Eliminar puntos viejos que salieron de la ventana
        while self.series.count() > 0:
            # Obtenemos el primer punto
            first_point = self.series.at(0)
            if first_point.x() < start_time:
                self.series.remove(0)
            else:
                break
        
        # Auto-escala en Y basada en los puntos visibles
        if self.series.count() > 0 and self.y_range is None:
            # Buscamos min y max Y manualmente iterando los puntos actuales
            points = self.series.points()
            if points:
                min_y = min(p.y() for p in points)
                max_y = max(p.y() for p in points)
                
                # Margen dinamico
                margin = (max_y - min_y) * 0.1 if max_y != min_y else 1.0
                
                # Seteamos el rango Y con un poco de "aire"
                self.axisY.setRange(max(0, min_y - margin), max_y + margin)

