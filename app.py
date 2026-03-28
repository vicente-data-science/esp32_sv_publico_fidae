from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn
import os

app = FastAPI()

# ==========================================
# 1. EL DASHBOARD HTML (La página web)
# ==========================================
html_dashboard = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Radar Espacial - Vicente Farias</title>
    <style>
        body { background-color: #111; color: white; text-align: center; font-family: Arial, sans-serif; }
        h1 { color: #00ffcc; }
        #monitor { border: 4px solid #333; border-radius: 10px; max-width: 100%; box-shadow: 0 0 20px #00ffcc; }
        .status { margin-top: 10px; font-weight: bold; }
    </style>
</head>
<body>
    <h1>🛰️ Monitor de Tracking Espacial 🛰️</h1>
    <img id="monitor" width="640" height="480" alt="Esperando video..." />
    <div id="estado" class="status" style="color: yellow;">Conectando al servidor...</div>

    <script>
        // Se conecta automáticamente al websocket usando la misma URL de la página
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = protocol + '//' + window.location.host + '/viewer';
        const ws = new WebSocket(wsUrl);
        const img = document.getElementById('monitor');
        const estado = document.getElementById('estado');

        ws.onopen = () => {
            estado.innerText = "Conectado. Esperando análisis de YOLO...";
            estado.style.color = "#00ffcc";
        };

        ws.onmessage = (event) => {
            // Convierte los bytes del video en imagen visible
            const urlCreator = window.URL || window.webkitURL;
            img.src = urlCreator.createObjectURL(event.data);
        };

        ws.onclose = () => {
            estado.innerText = "Desconectado del servidor.";
            estado.style.color = "red";
        };
    </script>
</body>
</html>
"""

# ==========================================
# 2. GESTIÓN DE CONEXIONES
# ==========================================
colab_clients = set()
esp32_clients = set()
viewer_clients = set()

# Ruta para entrar a la URL principal y ver la página
@app.get("/")
async def get_dashboard():
    return HTMLResponse(html_dashboard)

# Ruta WebSocket para Colab (Maneja JSON y Video procesado)
@app.websocket("/colab")
async def websocket_colab(websocket: WebSocket):
    await websocket.accept()
    colab_clients.add(websocket)
    try:
        while True:
            # FastAPI nos permite separar mágicamente si nos mandan texto o bytes
            message = await websocket.receive()
            if "text" in message:
                # JSON para los motores de la ESP32
                for esp in esp32_clients:
                    try: await esp.send_text(message["text"])
                    except: pass
            elif "bytes" in message:
                # Video procesado para la página web
                for viewer in viewer_clients:
                    try: await viewer.send_bytes(message["bytes"])
                    except: pass
    except WebSocketDisconnect:
        colab_clients.remove(websocket)

# Ruta WebSocket para la ESP32 (Solo sube video crudo)
@app.websocket("/esp32")
async def websocket_esp32(websocket: WebSocket):
    await websocket.accept()
    esp32_clients.add(websocket)
    try:
        while True:
            data = await websocket.receive_bytes()
            for colab in colab_clients:
                try: await colab.send_bytes(data)
                except: pass
    except WebSocketDisconnect:
        esp32_clients.remove(websocket)

# Ruta WebSocket para el Monitor de la página (Solo recibe video)
@app.websocket("/viewer")
async def websocket_viewer(websocket: WebSocket):
    await websocket.accept()
    viewer_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text() # Mantiene la conexión viva
    except WebSocketDisconnect:
        viewer_clients.remove(websocket)

# ==========================================
# 3. ARRANQUE DEL SERVIDOR
# ==========================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"Servidor FastAPI + WebSockets en puerto {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)import asyncio
import websockets
import os

# Listas para mantener los túneles abiertos
colab_clients = set()
esp32_clients = set()

# SINTAXIS ACTUALIZADA (Websockets >= 14.0)
async def handler(websocket):
    # Ahora el path se extrae de esta manera:
    path = websocket.request.path

    # Si Colab se conecta
    if path == "/colab":
        colab_clients.add(websocket)
        try:
            async for message in websocket:
                if isinstance(message, str): # Órdenes JSON para los motores
                    for esp in esp32_clients:
                        try:
                            await esp.send(message)
                        except:
                            pass
        finally:
            colab_clients.remove(websocket)

    # Si la ESP32 se conecta
    elif path == "/esp32":
        esp32_clients.add(websocket)
        try:
            async for message in websocket:
                if isinstance(message, bytes): # Foto en crudo
                    for colab in colab_clients:
                        try:
                            await colab.send(message)
                        except:
                            pass
        finally:
            esp32_clients.remove(websocket)

async def main():
    port = int(os.environ.get("PORT", 10000))
    print(f"Servidor WebSocket iniciado en el puerto {port}...")
    
    async with websockets.serve(handler, "0.0.0.0", port):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
