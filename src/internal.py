from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.ports import check_ports
from src.middleware.request_counter import RequestCounterMiddleware
from src.api.endpoint_device import router as device_router
from src.api.endpoint_system import router as system_router
from src.api.endpoint_home import router as home_router
from src.api.endpoint_security import router as security_router
from src.api.endpoint_webcam import router as webcam_router
from src.api.endpoint_misc import router as misc_router
from src.api.websocket_routes import router as ws_router
from fastapi.responses import RedirectResponse

import threading
from src.core.code import generated_code, display_code_window

available_port = check_ports()

SERVER_PORT = available_port

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestCounterMiddleware)

# Routers
app.include_router(device_router)
app.include_router(system_router)
app.include_router(home_router)
app.include_router(security_router)
app.include_router(webcam_router)
app.include_router(misc_router)
app.include_router(ws_router)

WHITE_BOLD = "\033[1;37m"
GREEN = "\033[0;32m"
BLUE = "\033[0;34m"
RESET = "\033[0m"

print(f"{WHITE_BOLD}Logs: Server started on port {SERVER_PORT}{RESET}")
print(f"{WHITE_BOLD}{GREEN}Dev Logs:{WHITE_BOLD} Tests available at {BLUE}http://localhost:{SERVER_PORT}/docs{RESET}")

@app.get("/")
async def root():
    return RedirectResponse(url="https://optifyx.thueshen.me/status/success")

def run_server():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SERVER_PORT)