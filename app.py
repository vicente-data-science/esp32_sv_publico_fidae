from flask import Flask, request, Response, jsonify

app = Flask(__name__)

# Variables globales para guardar lo último que llegue
ultimo_frame = None
ultimas_coordenadas = {"errorX": 0, "errorY": 0, "status": "esperando"}

@app.route('/')
def index():
    return "Servidor del Proyecto FIDAE Operativo", 200

# ---------------------------------------------------------
# ESTA ES LA RUTA QUE BUSCA EL ESP32 (La que da el 404 ahora)
# ---------------------------------------------------------
@app.route('/upload_frame', methods=['POST'])
def recibir_frame():
    global ultimo_frame
    # Guardamos los bytes de la imagen que envía el ESP32
    ultimo_frame = request.data
    print("Frame recibido del ESP32-CAM")
    return "OK", 200

# Ruta para que Google Colab descargue la foto
@app.route('/get_frame', methods=['GET'])
def enviar_frame():
    if ultimo_frame:
        return Response(ultimo_frame, mimetype='image/jpeg')
    return "No hay frames aún", 404

# Ruta para que Colab guarde los resultados de la IA
@app.route('/update_coords', methods=['POST'])
def actualizar_coords():
    global ultimas_coordenadas
    ultimas_coordenadas = request.json
    return jsonify({"status": "actualizado"}), 200

# Ruta para que el ESP32 de los servos lea qué hacer
@app.route('/get_coords', methods=['GET'])
def obtener_coords():
    return jsonify(ultimas_coordenadas), 200

if __name__ == "__main__":
    # Render usa el puerto 10000 por defecto
    app.run(host='0.0.0.0', port=10000)