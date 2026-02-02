import psutil
import time

while True:
    cores_usage = psutil.cpu_percent(interval=1, percpu=True)
    print("Cantidad de nucleos: ",psutil.cpu_count(logical=False))

    avg_usage = 0
    for usage in cores_usage:
        avg_usage += usage
    avg_usage /= len(cores_usage)
    print("Promedio de uso del CPU: ",avg_usage)

    
    time.sleep(1)