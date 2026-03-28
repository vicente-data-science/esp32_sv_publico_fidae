from flask import Flask, request, Response, jsonify

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
