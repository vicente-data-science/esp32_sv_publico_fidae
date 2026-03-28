from flask import Flask, request, Response

app = Flask(__name__)
foto_buffer = None

# 1. El ESP32 envía a la raíz (POST /)
@app.route('/', methods=['POST'])
def recibir():
    global foto_buffer
    foto_buffer = request.data  # Aquí se guarda la imagen en RAM
    return "OK", 200

# 2. El Colab pide a la raíz (GET /)
# CAMBIAMOS ESTO: Ahora la raíz también ENTREGA si es un GET
@app.route('/', methods=['GET'])
def entregar():
    global foto_buffer
    if foto_buffer is not None:
        return Response(foto_buffer, mimetype='image/jpeg')
    return "Servidor vacío. Esperando al ESP32...", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
