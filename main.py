import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QFrame, QPushButton,
    QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QScrollArea
)
from PySide6.QtCore import QTimer, Qt
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
            elif text == "Procesos":
                btn.clicked.connect(self.create_process_list)

        menuLayout.addStretch()

        # =========================
        # ARMAR UI
        # =========================
        mainLayout.addWidget(self.menuFrame)
        mainLayout.addWidget(self.contentFrame)

        # Timer para evitar el bloqueo de la UI
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_charts)

    def create_usage_charts(self, layout):
        # Obtener el layout directamente del frame
        layout = self.contentFrame.layout()
        
        # Limpiar lo que hubiera antes
        self.clear_layout(layout)

        # =========================
        # GRAFICOS
        # =========================
        self.cpu_chart = LinearChart("CPU Usage", y_range=(0, 100))
        self.mem_chart = LinearChart("Memory Usage", y_range=(0, 100))
        self.disk_chart = LinearChart("Disk Usage", y_range=(0, 100))
        self.net_chart = LinearChart("Network Usage")
        
        layout.addWidget(self.cpu_chart)
        layout.addWidget(self.mem_chart)
        layout.addWidget(self.disk_chart)
        layout.addWidget(self.net_chart)
        
        # Iniciar actualización periódica (cada 100ms)
        if not self.timer.isActive():
            self.timer.start(100)
  
    def create_process_list(self, layout):
        # Detener el timer porque update_charts fallará si no están los gráficos
        self.timer.stop()

        # Obtener el layout directamente del frame
        layout = self.contentFrame.layout()
        
        # Limpiar lo que hubiera antes
        self.clear_layout(layout)
        
        # =========================
        # LISTA DE PROCESOS (Scroll Area)
        # =========================
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        # Estilo para que no se vea el borde del scroll area si no se quiere
        scroll.setFrameShape(QFrame.NoFrame)
        
        container = QWidget()
        scroll.setWidget(container)
        
        # Grid dentro del container del scroll
        grid = QGridLayout(container)
        grid.setAlignment(Qt.AlignTop) # Para que las filas no se expandan verticalmente
        
        layout.addWidget(scroll)

        pids = psutil.pids()
        procesos_info = []
        
        # Use oneshot para optimizar si es posible, pero simple por ahora.
        # Lo más importante es interval=0 o None para NO BLOQUEAR.
        for pid in pids:
            try:
                proceso = psutil.Process(pid)
                # interval=0.0 o None devuelve el valor inmediato (no bloqueante)
                # La primera vez puede dar 0.0 si no se ha medido antes.
                cpu = proceso.cpu_percent(interval=None) 
                
                info = {
                    'pid': pid,
                    'nombre': proceso.name(),
                    'usuario': proceso.username(),
                    'cpu_percent': cpu,
                    'mem_rss': proceso.memory_info().rss / (1024 * 1024) # MB
                }
                procesos_info.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Opcional: ordenar por uso de memoria
        procesos_info.sort(key=lambda x: x['mem_rss'], reverse=True)

        # Headers
        headers = ["PID", "Nombre", "Usuario", "CPU %", "Memoria (MB)"]
        for col, h in enumerate(headers):
            lbl = QLabel(f"<b>{h}</b>")
            lbl.setStyleSheet("color: white; font-size: 14px;")
            grid.addWidget(lbl, 0, col)

        for i, proceso in enumerate(procesos_info):
            row = i + 1
            # Estilo alterno o simple
            
            grid.addWidget(QLabel(str(proceso['pid'])), row, 0)
            grid.addWidget(QLabel(proceso['nombre']), row, 1)
            grid.addWidget(QLabel(proceso['usuario']), row, 2)
            grid.addWidget(QLabel(f"{proceso['cpu_percent']:.1f}%"), row, 3)
            grid.addWidget(QLabel(f"{proceso['mem_rss']:.1f} MB"), row, 4)
            
        # NO reiniciamos el timer aquí porque este método no actualiza en tiempo real por ahora

    def update_charts(self):
        # Verificar que los graficos existan antes de actualizar
        if not hasattr(self, 'cpu_chart'):
            return

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
        
        # print(f"Update: CPU={avg_cpu:.1f}% MEM={mem_usage}% NET={net_sent_speed:.2f}MB/s")
        
        # 3. Actualizar Graficos (Todos usan el mismo tiempo 'now')
        if hasattr(self, 'cpu_chart'): self.cpu_chart.add_data_point(now, avg_cpu)
        if hasattr(self, 'mem_chart'): self.mem_chart.add_data_point(now, mem_usage)
        #self.gpu_chart.add_data_point(now) 
        if hasattr(self, 'disk_chart'): self.disk_chart.add_data_point(now, disk_usage)
        if hasattr(self, 'net_chart'): self.net_chart.add_data_point(now, net_sent_speed)

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
