import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QFrame, QPushButton,
    QHBoxLayout, QVBoxLayout
)
from linearChart import LinearChart


class SystemMonitor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Monitor de recursos del sistema")
        self.resize(800, 600)

        # =========================
        # CENTRAL WIDGET
        # =========================
        central = QWidget(self)
        self.setCentralWidget(central)

        mainLayout = QHBoxLayout(central)
        mainLayout.setContentsMargins(0, 0, 0, 0)

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

        menuLayout.addStretch()

        # =========================
        # CONTENIDO
        # =========================
        self.contentFrame = QFrame()
        self.contentFrame.setStyleSheet("background-color: #7A7A7A;")

        contentLayout = QVBoxLayout(self.contentFrame)
        contentLayout.setContentsMargins(10, 10, 10, 10)
        contentLayout.setSpacing(10)

        # =========================
        # GRAFICO CPU
        # =========================
        self.cpu_chart = LinearChart("CPU Usage")
        self.mem_chart = LinearChart("Memory Usage")
        self.gpu_chart = LinearChart("GPU Usage")
        self.disk_chart = LinearChart("Disk Usage")
        self.net_chart = LinearChart("Network Usage")
    

        contentLayout.addWidget(self.cpu_chart)
        contentLayout.addWidget(self.mem_chart)
        contentLayout.addWidget(self.gpu_chart)
        contentLayout.addWidget(self.disk_chart)
        contentLayout.addWidget(self.net_chart)

        # =========================
        # ARMAR UI
        # =========================
        mainLayout.addWidget(self.menuFrame)
        mainLayout.addWidget(self.contentFrame)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SystemMonitor()
    window.show()
    sys.exit(app.exec())
