from flask import Flask, request, Response, jsonify

app = Flask(__name__)

# Memoria volátil para la imagen
ultimo_frame = None

# CAMBIO CRÍTICO: Ahora aceptamos POST en la raíz '/'
@app.route('/', methods=['GET', 'POST'])
def handle_root():
    global ultimo_frame
    if request.method == 'POST':
        # Aquí recibimos la foto del ESP32
        ultimo_frame = request.data
        print("¡Imagen recibida en la raíz!")
        return "OK", 200
    else:
        # Si entras desde el navegador, ves esto
        return "Servidor FIDAE: Operativo y esperando fotos.", 200

@app.route('/get_frame', methods=['GET'])
def get_frame():
    if ultimo_frame:
        return Response(ultimo_frame, mimetype='image/jpeg')
    return "Aún no hay fotos", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)