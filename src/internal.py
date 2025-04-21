from fastapi import FastAPI
from src.core.ports import check_ports
from src.middleware.request_counter import RequestCounterMiddleware
from src.api.endpoint_device import router as device_router
from src.api.endpoint_system import router as system_router
from src.api.endpoint_home import router as home_router
from src.api.endpoint_security import router as security_router
from src.api.endpoint_webcam import router as webcam_router
from src.api.endpoint_misc import router as misc_router
from src.api.websocket_routes import router as ws_router

import threading
from src.core.code import generated_code, display_code_window

app = FastAPI()

app.add_middleware(RequestCounterMiddleware)

# Routers
app.include_router(device_router)
app.include_router(system_router)
app.include_router(home_router)
app.include_router(security_router)
app.include_router(webcam_router)
app.include_router(misc_router)
app.include_router(ws_router)

available_port = check_ports()

print(f"Logs: Server started on port {available_port}")

# Inicialização do Servidor
def run_server():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=available_port)