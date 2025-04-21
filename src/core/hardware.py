import psutil
import GPUtil
import subprocess
import speedtest
import time

def get_internet_speed():
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download() / 1_000_000
        upload_speed = st.upload() / 1_000_000
        return {
            "download_speed": f"{download_speed:.2f} Mbps",
            "upload_speed": f"{upload_speed:.2f} Mbps",
        }
    except AttributeError:
        return {"error": "Speedtest module corrupted - reinstall speedtest-cli"}
    except Exception as e:
        return {"error": f"Speedtest failed: {str(e)}"}

def get_gpu_info():
    try:
        gpus = GPUtil.getGPUs()
        if not gpus:
            return {"gpu": "No GPU detected"}
        gpu = gpus[0]
        return {
            "gpu_name": gpu.name,
            "gpu_load": f"{gpu.load * 100:.2f}%",
            "gpu_memory_free": f"{gpu.memoryFree} MB",
            "gpu_memory_used": f"{gpu.memoryUsed} MB",
            "gpu_memory_total": f"{gpu.memoryTotal} MB",
            "gpu_temperature": f"{gpu.temperature} °C",
        }
    except Exception as e:
        return {"gpu_error": f"Failed to get GPU info: {str(e)}"}

def check_bluetooth_status() -> str:
    try:
        output = subprocess.check_output(
            ["powershell", "-Command", "Get-PnpDevice -Class Bluetooth"],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if "True" in output or "OK" in output:
            return "Bluetooth is ON"
        else:
            return "Bluetooth is OFF"
    except Exception as e:
        return f"Error checking Bluetooth: {str(e)}"

def get_home_realtime():
    internet_speed = get_internet_speed()
    bluetooth_status = check_bluetooth_status()
    net_io = psutil.net_io_counters()
    uptime_hours = (time.time() - psutil.boot_time()) / 3600
    uptime_formatted = f"{uptime_hours:.2f} hours"
    return {
        "network_usage": f"↑{net_io.bytes_sent/1e6:.1f}MB ↓{net_io.bytes_recv/1e6:.1f}MB",
        **internet_speed,
        "bluetooth": bluetooth_status,
        "uptime": f"{uptime_formatted}"
    }

def get_system_realtime():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    gpu_info = get_gpu_info()
    return {
        "cpu": f"{cpu}%",
        **gpu_info,
        "ram": f"{ram}%",
        "processes": len(psutil.pids())
    }

def get_disk_realtime():
    disk_usage = psutil.disk_usage('/')
    return {
        "disk_usage": f"{disk_usage.percent}%",
        "disk_total": f"{disk_usage.total / (1024 ** 3):.2f} GB",
        "disk_free": f"{disk_usage.free / (1024 ** 3):.2f} GB",
        "disk_used": f"{disk_usage.used / (1024 ** 3):.2f} GB"
    }