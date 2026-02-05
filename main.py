import sys, os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QFrame, QPushButton,
    QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QMenu
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

        for text in ["Recursos", "processs", "Componentes", "Temperaturas"]:
            btn = QPushButton(text)
            btn.setFixedHeight(50)
            btn.setStyleSheet("background-color: #5A5A5A;")
            menuLayout.addWidget(btn)

            if text == "Recursos":
                # Conectar sin pasar argumentos extra que confundan (el booleano de clicked)
                btn.clicked.connect(self.create_usage_charts)
            elif text == "processs":
                btn.clicked.connect(self.create_process_list)

        menuLayout.addStretch()

        # =========================
        # ARMAR UI
        # =========================
        mainLayout.addWidget(self.menuFrame)
        mainLayout.addWidget(self.contentFrame)

        # Timer para evitar el bloqueo de la UI
        self.chart_timer = QTimer()
        self.chart_timer.timeout.connect(self.update_charts)

        self.process_timer = QTimer()
        self.process_timer.timeout.connect(self.update_process_list)    

    def create_usage_charts(self, layout):
        # Obtener el layout directamente del frame
        layout = self.contentFrame.layout()
        
        # Limpiar lo que hubiera antes
        self.clear_layout(layout)

        # =========================
        # GRAFICOS
        # =========================
        self.cpu_chart = LinearChart("CPU Usage (avg)", y_range=(0, 100))
        self.mem_chart = LinearChart("Memory Usage", y_range=(0, 100))
        self.disk_chart = LinearChart("Disk Usage", y_range=(0, 100))
        self.net_chart = LinearChart("Network Usage")
        
        layout.addWidget(self.cpu_chart)
        layout.addWidget(self.mem_chart)
        layout.addWidget(self.disk_chart)
        layout.addWidget(self.net_chart)
        
        # Iniciar actualización periódica (cada 100ms)
        if not self.chart_timer.isActive():
            self.chart_timer.start(100)
  
    def create_process_list(self):
        # Detener el timer de graficos
        self.chart_timer.stop()

        # Obtener el layout directamente del frame
        layout = self.contentFrame.layout()
        
        # Limpiar lo que hubiera antes
        self.clear_layout(layout)
        
        # =========================
        # LISTA DE PROCESOS (Tabla)
        # =========================
        self.table = QTableWidget()
        layout.addWidget(self.table)
        
        # Configurar columnas
        headers = ["PID", "Name", "User", "% CPU", "Memory usage"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        
        # Estilo de tabla
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #333;
                color: white;
                gridline-color: #555;
                font-family: Arial;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #444;
                color: white;
                padding: 4px;
                border: 1px solid #555;
            }
        """)
        
        # Propiedades de comportamiento
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        # Cargar primera vez
        self.update_process_list()
        
        # Iniciar actualización periódica (cada 3 segundos para no saturar)
        if not self.process_timer.isActive():
            self.process_timer.start(3000)

    def update_process_list(self, process_info=None):
        if process_info is None:
            process_info = self.find_process_info()

         # Llenar tabla
        # Guardar scroll actual para intentar mantenerlo (opcional, mejora UX)
        current_scroll = self.table.verticalScrollBar().value()
        
        self.table.setRowCount(len(process_info))
        for row, info in enumerate(process_info):

            # PID
            self.table.setItem(row, 0, QTableWidgetItem(str(info['PID'])))
            # Name
            self.table.setItem(row, 1, QTableWidgetItem(str(info['Name'])))
            # User
            self.table.setItem(row, 2, QTableWidgetItem(str(info['User'])))
            # CPU
            self.table.setItem(row, 3, QTableWidgetItem(f"{info['% CPU']:.1f}%"))
            # Memoria
            self.table.setItem(row, 4, QTableWidgetItem(f"{info['Memory usage']:.1f} MB"))
            
        self.table.verticalScrollBar().setValue(current_scroll)

    def find_process_info(self, order_by=None):
        pids = psutil.pids()
        process_info = []   
        for pid in pids:
            try:
                process = psutil.Process(pid)
                # interval=None devuelve el valor inmediato
                cpu = process.cpu_percent(interval=None) 
                
                info = {
                    'PID': pid,
                    'Name': process.name(),
                    'User': process.username(),
                    '% CPU': cpu,
                    'Memory usage': process.memory_info().rss / (1024 * 1024) # MB
                }
                process_info.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Opcional: ordenar por uso de memoria
        if order_by == "Memory":
            process_info.sort(key=lambda x: x['Memory usage'], reverse=True)
        elif order_by == "CPU":
            process_info.sort(key=lambda x: x['% CPU'], reverse=True)
        elif order_by == "PID":
            process_info.sort(key=lambda x: x['PID'], reverse=True)
        elif order_by == "Name":
            process_info.sort(key=lambda x: x['Name'], reverse=True)
        elif order_by == "User":
            process_info.sort(key=lambda x: x['User'], reverse=True)
        
        # Por defecto ordenar por memoria si no se especifica, para que se vea interesante
        if order_by is None:
             process_info.sort(key=lambda x: x['Memory usage'], reverse=True)
             
        return process_info

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
        
        # 3. Actualizar Graficos (Todos usan el mismo tiempo 'now')
        if hasattr(self, 'cpu_chart'): self.cpu_chart.add_data_point(now, avg_cpu)
        if hasattr(self, 'mem_chart'): self.mem_chart.add_data_point(now, mem_usage)
        if hasattr(self, 'disk_chart'): self.disk_chart.add_data_point(now, disk_usage)
        if hasattr(self, 'net_chart'): self.net_chart.add_data_point(now, net_sent_speed)
    
    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

    def show_context_menu(self, position):
        item = self.table.itemAt(position)
        print(item)
        if item is None:
            return

        fila = item.row()
        pid = self.table.item(fila,0).text()

        menu = QMenu(self)
        menu.addAction("Kill Process", lambda: self.kill_process(pid))
        menu.exec(self.table.mapToGlobal(position))
        process_info = self.find_process_info()
        self.update_process_list(process_info)

    def kill_process(self, pid):
        try:
            os.kill(int(pid), 9)
        except Exception as e:
            print(f"Error al matar el proceso: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SystemMonitor()
    window.show()
    sys.exit(app.exec())
