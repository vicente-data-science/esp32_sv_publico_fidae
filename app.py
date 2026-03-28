import asyncio
import websockets

# Listas para mantener los túneles abiertos
colab_clients = set()
esp32_clients = set()

async def handler(websocket, path):
    # Si Colab se conecta, lo metemos a su grupo
    if path == "/colab":
        colab_clients.add(websocket)
        try:
            async for message in websocket:
                # Si Colab envía texto (JSON de los servos), se lo reenviamos al ESP32
                if isinstance(message, str):
                    for esp in esp32_clients:
                        try:
                            await esp.send(message)
                        except:
                            pass
        finally:
            colab_clients.remove(websocket)

    # Si la ESP32 se conecta, la metemos a su grupo
    elif path == "/esp32":
        esp32_clients.add(websocket)
        try:
            async for message in websocket:
                # Si la ESP32 envía bytes (la foto), se la reenviamos a Colab
                if isinstance(message, bytes):
                    for colab in colab_clients:
                        try:
                            await colab.send(message)
                        except:
                            pass
        finally:
            esp32_clients.remove(websocket)

print("Servidor WebSocket iniciado en puerto 10000...")
start_server = websockets.serve(handler, "0.0.0.0", 10000)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()from flask import Flask, request, Response, jsonify

app = Flask(__name__)

# --- MEMORIA RAM DEL SERVIDOR ---
foto_buffer = None
# Variables globales para guardar la distancia de los motores
servo_data = {
    "servo_pan": 0,  # Eje X (Izquierda/Derecha)
    "servo_tilt": 0  # Eje Y (Arriba/Abajo)
}

# ==========================================
# RUTAS PARA LA CÁMARA (FOTOS)
# ==========================================

# 1. El ESP32 deposita la foto aquí
@app.route('/', methods=['POST'])
def recibir_foto():
    global foto_buffer
    foto_buffer = request.data
    return "OK", 200

# 2. La IA de Colab retira la foto aquí
@app.route('/', methods=['GET'])
def entregar_foto():
    global foto_buffer
    if foto_buffer is not None:
        return Response(foto_buffer, mimetype='image/jpeg')
    return "Sin foto", 404

# ==========================================
# RUTAS PARA LOS MOTORES (SERVOS)
# ==========================================

# 3. La IA de Colab deposita el cálculo de los motores aquí
@app.route('/mover_servos', methods=['POST'])
def recibir_coordenadas():
    global servo_data
    datos = request.get_json() # Recibimos el JSON de Colab
    
    if datos:
        # Guardamos los deltas calculados por la IA
        servo_data['servo_pan'] = datos.get('servo_pan', 0)
        servo_data['servo_tilt'] = datos.get('servo_tilt', 0)
        return jsonify({"status": "Coordenadas actualizadas"}), 200
        
    return jsonify({"error": "Formato JSON incorrecto"}), 400

# 4. El ESP32 retira las coordenadas para mover sus motores
@app.route('/mover_servos', methods=['GET'])
def entregar_coordenadas():
    global servo_data
    # Entregamos el JSON exacto al ESP32
    return jsonify(servo_data), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
