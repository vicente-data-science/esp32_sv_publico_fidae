from flask import Flask, request, jsonify

app = Flask(__name__)

# Aquí guardaremos los datos temporalmente en la memoria del servidor
# Para la simulación inicial de una sola unidad, una lista simple funciona perfecto.
registro_datos = []


@app.route('/ingresar_datos', methods=['POST'])
def recibir_datos():
    # El ESP32 enviará los datos en formato JSON
    datos_nuevos = request.json

    # Agregamos los datos a nuestro registro
    registro_datos.append(datos_nuevos)

    print(f"Datos recibidos: {datos_nuevos}")
    return jsonify({"mensaje": "Datos guardados correctamente", "status": "ok"}), 201

@app.route('/obtener_datos', methods=['GET'])
def enviar_datos():
    # Colab usará esta ruta para descargar todo el registro
    return jsonify(registro_datos), 200

if __name__ == '__main__':
    # El puerto 10000 es el estándar que suele usar Render
    app.run(host='0.0.0.0', port=10000)