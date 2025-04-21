import json
import random
import string
import io
import cv2
import psutil
import socket
import threading
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import tkinter as tk
import GPUtil
import subprocess
import speedtest
import serial
import serial.tools.list_ports
import requests
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
import pyperclip
import time

app = FastAPI()

ports = [8080, 3000, 5000]

request_counts = defaultdict(int)

class RequestCounterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        if response.status_code == 200:
            request_counts["requests_success"] += 1
        elif 400 <= response.status_code < 500:
            request_counts["requests_malformed"] += 1
        elif 500 <= response.status_code < 600:
            request_counts["requests_bad"] += 1
        
        return response

app.add_middleware(RequestCounterMiddleware)

def check_ports():
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('0.0.0.0', port))
            sock.close()
            return port
        except OSError:
            pass
    raise Exception("No available ports to start the server.")

generated_code = ""

def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def copy_to_clipboard(code):
    pyperclip.copy(code)

def convert_nmea_to_decimal(value: str, direction: str):
    if not value or not direction:
        return "Not Available"

    degrees = int(value[:2])
    minutes = float(value[2:])
    decimal = degrees + (minutes / 60)

    if direction in ['S', 'W']:
        decimal = -decimal

    return round(decimal, 6)

def parse_nmea_data(nmea_sentence: str):
    if nmea_sentence.startswith('$GPGGA') or nmea_sentence.startswith('$GPRMC'):
        parts = nmea_sentence.split(',')
        try:
            if nmea_sentence.startswith('$GPRMC'):
                lat = convert_nmea_to_decimal(parts[3], parts[4])
                lon = convert_nmea_to_decimal(parts[5], parts[6])
            elif nmea_sentence.startswith('$GPGGA'):
                lat = convert_nmea_to_decimal(parts[2], parts[3])
                lon = convert_nmea_to_decimal(parts[4], parts[5])
            else:
                return {"error": "Unsupported NMEA format"}

            return {"latitude": lat, "longitude": lon}
        except (IndexError, ValueError):
            return {"error": "Malformed NMEA data"}
    else:
        return {"error": "Unsupported NMEA sentence"}

def get_gps_data_from_device(port: str, baudrate: int = 9600, timeout: int = 2):
    try:
        with serial.Serial(port, baudrate, timeout=timeout) as ser:
            while True:
                line = ser.readline().decode('ascii', errors='ignore').strip()
                if line.startswith('$GPGGA') or line.startswith('$GPRMC'):
                    return parse_nmea_data(line)
    except Exception as e:
        return {"error": f"Failed to read GPS data from {port}: {str(e)}"}

def detect_gps_device():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        try:
            if "GPS" in port.description or "GNSS" in port.description:
                gps_data = get_gps_data_from_device(port.device)
                if gps_data and "latitude" in gps_data and "longitude" in gps_data:
                    return gps_data
        except Exception as e:
            continue
    return None

def get_public_ip():
    try:
        response = requests.get("https://api64.ipify.org?format=json", timeout=5)
        response.raise_for_status()
        ip_data = response.json()
        return {"public_ip": ip_data.get("ip", "Not Available")}
    except Exception as e:
        return {"error": f"Failed to fetch public IP: {str(e)}"}

def display_code_window(code):
    root = tk.Tk()
    root.title("Connection Code")
    root.geometry("600x250")

    root.attributes('-topmost', True)
    root.lift()
    root.focus_force()

    label = tk.Label(root, text=f"Connection Code: {code}", font=("Arial", 20))
    label.pack(pady=20)

    copy_button = tk.Button(root, text="Copy Code", command=lambda: copy_to_clipboard(code))
    copy_button.pack(pady=10)

    root.mainloop()

available_port = check_ports()
print(f"Logs: Server started on port {available_port}")

@app.get("/check_online_connections")
async def check_online_connections():
    try:
        return {"status": "Online"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/start_device")
async def start_device():
    try:
        global generated_code
        generated_code = generate_code()
        
        threading.Thread(target=display_code_window, args=(generated_code,)).start()

        return {"message": "Device started! A code is displayed on the screen."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class CodeRequest(BaseModel):
    code: str

@app.post("/connection_code")
async def connection_code(request: Request, data: CodeRequest):
    try:
        if data.code == generated_code:
            return {"message": "Connection authorized!"}
        else:
            raise HTTPException(status_code=400, detail="Invalid code!")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/webcam_check")
async def webcam_check():
    try:
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            raise HTTPException(status_code=500, detail="Unable to access the webcam")

        ret, frame = cap.read()

        cap.release()

        if not ret:
            raise HTTPException(status_code=500, detail="Failed to capture image")

        _, img_encoded = cv2.imencode('.webp', frame)

        img_bytes = img_encoded.tobytes()

        return StreamingResponse(io.BytesIO(img_bytes), media_type="image/webp")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

@app.get("/public_ip")
async def public_ip():
    try:
        response = requests.get("https://api64.ipify.org?format=json", timeout=5)
        response.raise_for_status()
        ip_data = response.json()
        return {"public_ip": ip_data.get("ip", "Not Available")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/security_realtime")
async def get_security_realtime():
    try:
        gps_data = detect_gps_device()
        if not gps_data:
            gps_data = get_public_ip()

        battery = psutil.sensors_battery()

        return {
            "battery": f"{battery.percent}%" if battery else "Not Available",
            "location": gps_data,
            "requests_success": request_counts["requests_success"],
            "requests_malformed": request_counts["requests_malformed"],
            "requests_bad": request_counts["requests_bad"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/home_realtime")
async def home_realtime():
    try:
        return get_home_realtime()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system_realtime")
async def system_realtime():
    try:
        return get_system_realtime()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/disk_realtime")
async def disk_realtime():
    try:
        return get_disk_realtime()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        while True:
            data = await websocket.receive_text()
            if data == "/home_realtime":
                response = get_home_realtime()
            elif data == "/system_realtime":
                response = get_system_realtime()
            elif data == "/disk_realtime":
                response = get_disk_realtime()
            elif data == "/security_realtime":
                response = get_security_realtime()
            else:
                response = {"error": "Invalid command"}
            await websocket.send_text(json.dumps(response))
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_text(json.dumps({"error": str(e)}))

# Inicialização do Servidor
def run_server():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=available_port)