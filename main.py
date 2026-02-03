import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QFrame, QPushButton,
    QHBoxLayout, QVBoxLayout
)
from PySide6.QtCore import QTimer
from linearChart import LinearChart
import psutil
import time



class SystemMonitor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Monitor de recursos del sistema")
        self.resize(800, 800)

        # =========================
        # CENTRAL WIDGET
        # =========================
        central = QWidget(self)
        self.setCentralWidget(central)

        mainLayout = QHBoxLayout(central)
        mainLayout.setContentsMargins(0, 0, 0, 0)

        # =========================
        # CONTENIDO
        # =========================
        self.contentFrame = QFrame()
        self.contentFrame.setStyleSheet("background-color: #7A7A7A;")

        contentLayout = QVBoxLayout(self.contentFrame)
        contentLayout.setContentsMargins(10, 10, 10, 10)
        contentLayout.setSpacing(10)



        # =========================
        # MENU LATERAL
        # =========================
        self.menuFrame = QFrame()
        self.menuFrame.setFixedWidth(150)
        self.menuFrame.setStyleSheet("background-color: #4A4A4A;")

        menuLayout = QVBoxLayout(self.menuFrame)
        menuLayout.setContentsMargins(0, 10, 0, 0)
        menuLayout.setSpacing(10)

        for text in ["Recursos", "Procesos", "Componentes", "Temperaturas"]:
            btn = QPushButton(text)
            btn.setFixedHeight(50)
            btn.setStyleSheet("background-color: #5A5A5A;")
            menuLayout.addWidget(btn)

            if text == "Recursos":
                # Conectar sin pasar argumentos extra que confundan (el booleano de clicked)
                btn.clicked.connect(self.create_usage_charts)

        menuLayout.addStretch()

        # =========================
        # ARMAR UI
        # =========================
        mainLayout.addWidget(self.menuFrame)
        mainLayout.addWidget(self.contentFrame)

        # Timer para evitar el bloqueo de la UI
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_charts)

    def create_usage_charts(self):
        # Obtener el layout directamente del frame
        layout = self.contentFrame.layout()
        
        # Limpiar lo que hubiera antes
        self.clear_layout(layout)

        # =========================
        # GRAFICOS
        # =========================
        self.cpu_chart = LinearChart("CPU Usage", y_range=(0, 100))
        self.mem_chart = LinearChart("Memory Usage", y_range=(0, 100))
        self.gpu_chart = LinearChart("GPU Usage", y_range=(0, 100))
        self.disk_chart = LinearChart("Disk Usage", y_range=(0, 100))
        self.net_chart = LinearChart("Network Usage")
        
        layout.addWidget(self.cpu_chart)
        layout.addWidget(self.mem_chart)
        layout.addWidget(self.gpu_chart)
        layout.addWidget(self.disk_chart)
        layout.addWidget(self.net_chart)
        
        # Iniciar actualización periódica (cada 1000ms = 1s)
        if not self.timer.isActive():
            self.timer.start(100)

    
    def update_charts(self):
        # interval=0 es vital para que no bloquee la interfaz
        
        # 1. Obtener datos
        cores_usage = psutil.cpu_percent(interval=0, percpu=True)
        mem_usage = psutil.virtual_memory().percent
        # Disk usage: Espacio ocupado (Linea plana)
        disk_usage = psutil.disk_usage('/').percent
        
        # Network: Calcular velocidad (Diferencia / tiempo)
        net_io = psutil.net_io_counters()
        now = time.time()
        
        net_sent_speed = 0
        if hasattr(self, 'last_net_io') and hasattr(self, 'last_time'):
            # Calculamos delta
            dt = now - self.last_time
            if dt > 0:
                net_sent_speed = (net_io.bytes_sent - self.last_net_io.bytes_sent) / dt / 1024 / 1024 # MB/s
        
        # Guardar estado para la proxima
        self.last_net_io = net_io
        self.last_time = now

        # 2. Calcular promedios/totales
        avg_cpu = sum(cores_usage) / len(cores_usage) if cores_usage else 0
        
        print(f"Update: CPU={avg_cpu:.1f}% MEM={mem_usage}% NET={net_sent_speed:.2f}MB/s")
        
        # 3. Actualizar Graficos (Todos usan el mismo tiempo 'now')
        self.cpu_chart.add_data_point(now, avg_cpu)
        self.mem_chart.add_data_point(now, mem_usage)
        # self.gpu_chart.add_data_point(now, psutil.gpu_percent(interval=0)) 
        self.disk_chart.add_data_point(now, disk_usage)
        self.net_chart.add_data_point(now, net_sent_speed)


    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SystemMonitor()
    window.show()
    sys.exit(app.exec())
