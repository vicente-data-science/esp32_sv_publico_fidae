import asyncio
import websockets
import os

# Listas para mantener los túneles abiertos
colab_clients = set()
esp32_clients = set()

async def handler(websocket, path):
    # Si Colab se conecta
    if path == "/colab":
        colab_clients.add(websocket)
        try:
            async for message in websocket:
                if isinstance(message, str): # JSON de servos
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
                if isinstance(message, bytes): # Foto cruda
                    for colab in colab_clients:
                        try:
                            await colab.send(message)
                        except:
                            pass
        finally:
            esp32_clients.remove(websocket)

async def main():
    # Render asigna el puerto dinámicamente, lo capturamos aquí
    port = int(os.environ.get("PORT", 10000))
    print(f"Servidor WebSocket iniciado en el puerto {port}...")
    
    async with websockets.serve(handler, "0.0.0.0", port):
        await asyncio.Future()  # Mantiene el servidor corriendo por siempre

if __name__ == "__main__":
    asyncio.run(main())
