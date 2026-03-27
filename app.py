from flask import Flask, request, Response, jsonify

app = Flask(__name__)

# Memoria temporal RAM (Render guardará solo lo más reciente)
ul ultimo_frame = None
ultimas_coordenadas = {"errorX": 0, "errorY": 0, "status": "buscando"}

# ---------------------------------------------------------
# PUERTAS PARA EL ESP32-CAM (EL OJO)
# ---------------------------------------------------------
@app.route('/upload_frame', methods=['POST'])
def recibir_video():
    global ultimo_frame
    ultimo_frame = request.data # Recibe los bytes del JPEG
    return "Frame recibido", 200

# ---------------------------------------------------------
# PUERTAS PARA GOOGLE COLAB (EL CEREBRO)
# ---------------------------------------------------------
@app.route('/get_frame', methods=['GET'])
def entregar_frame_a_colab():
    if ultimo_frame:
        return Response(ultimo_frame, mimetype='image/jpeg')
    return "Sin video", 404

@app.route('/update_coords', methods=['POST'])
def recibir_calculo_de_colab():
    global ultimas_coordenadas
    ultimas_coordenadas = request.json # Recibe el cálculo de la IA
    return "Coordenadas actualizadas", 200

# ---------------------------------------------------------
# PUERTA PARA EL ESP32 DE LOS SERVOS (EL MÚSCULO)
# ---------------------------------------------------------
@app.route('/get_coords', methods=['GET'])
def entregar_coordenadas_a_motores():
    return jsonify(ultimas_coordenadas), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)