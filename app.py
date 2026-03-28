import asyncio
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
