import unittest
import requests
import threading
import time
from src.internal import run_server

BASE_URL = "http://127.0.0.1:8080"  # Main port for the server

endpoints = {
    "POST /start_device": lambda: requests.post(f"{BASE_URL}/start_device"),
    "POST /connection_code": lambda: requests.post(f"{BASE_URL}/connection_code"),
    "GET /system_realtime": lambda: requests.get(f"{BASE_URL}/system_realtime"),
    "GET /disk_realtime": lambda: requests.get(f"{BASE_URL}/disk_realtime"),
    "GET /home_realtime": lambda: requests.get(f"{BASE_URL}/home_realtime"),
    "GET /security_realtime": lambda: requests.get(f"{BASE_URL}/security_realtime"),
    "GET /webcam_check": lambda: requests.get(f"{BASE_URL}/webcam_check"),
    "GET /public_ip": lambda: requests.get(f"{BASE_URL}/public_ip"),
    "GET /check_online_connections": lambda: requests.get(f"{BASE_URL}/check_online_connections"),
}

class TestEndpoints(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.server_thread = threading.Thread(target=run_server, daemon=True)
        cls.server_thread.start()
        time.sleep(3)

    def test_endpoints(self):
        for name, request_func in endpoints.items():
            with self.subTest(endpoint=name):
                if name == "POST /connection_code":
                    self.skipTest(f"{name} skipped because it requires a valid code.")
                try:
                    response = request_func()
                    self.assertTrue(response.status_code in [200, 201], f"{name} failed with status code {response.status_code}")
                except Exception as e:
                    self.fail(f"{name} raised an exception: {e}")

if __name__ == "__main__":
    unittest.main()
