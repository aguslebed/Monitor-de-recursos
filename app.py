import psutil
import time

while True:
    print("Porcentaje de uso del CPU: ",psutil.cpu_percent(interval=1, percpu=True))
    print("Cantidad de nucleos: ",psutil.cpu_count(logical=False))
    time.sleep(1)