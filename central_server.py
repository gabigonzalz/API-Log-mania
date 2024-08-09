from flask import Flask, request, jsonify, render_template,redirect
import sqlite3
import threading

app = Flask(__name__)

# API Key fija
VALID_API_KEY = 'fc15c9c6-c08e-4cb5-b84b-c81f8eb4d876'

# Crea un Lock para la conexión a la base de datos
db_lock = threading.Lock()

# Acepta logs y valida la api key
@app.route('/log', methods=['POST'])
def log():
    # Verifica el encabezado Authorization
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Verifica el API KEY
    api_key = auth_header.split(' ')[1]
    if api_key != VALID_API_KEY:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Guardamos los datos recibidos
    data = request.json
    timestamp = data.get('timestamp')
    name = data.get('name')
    levelname = data.get('levelname')
    message = data.get('message')

    # Usar el Lock para asegurar acceso seguro a la base de datos
    with db_lock:
        with sqlite3.connect('logs.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO logs (timestamp, name, levelname, message)
                VALUES (?, ?, ?, ?)
            ''', (timestamp, name, levelname, message))
            conn.commit()

    return jsonify({'status': 'success'}), 200


# Ruta para redirigir la raíz a /service1
@app.route('/')
def root_redirect():
    return redirect('/logs')

# Ruta para mostrar todos los logs sin filtrado
@app.route('/logs')
def all_logs():
    with db_lock:
        with sqlite3.connect('logs.db') as conn:
            conn.row_factory = sqlite3.Row  # Esto hace que fetchall devuelva una lista de diccionarios
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM logs')
            logs = cursor.fetchall()
    return render_template('logs.html', logs=logs)

## Ruta para mostrar logs filtrados por timestamp
@app.route('/logs/timestamp')
def logs_by_timestamp():
    with db_lock:
        with sqlite3.connect('logs.db') as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM logs_by_timestamp')
            logs = cursor.fetchall()
    return render_template('logs.html', logs=logs)

# Ruta para mostrar logs filtrados por received_at
@app.route('/logs/received')
def logs_by_received():
    with db_lock:
        with sqlite3.connect('logs.db') as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM logs_by_receive')
            logs = cursor.fetchall()
    return render_template('logs.html', logs=logs)

# Ruta para mostrar logs filtrados por levelname
@app.route('/logs/levelname')
def logs_by_levelname():
    with db_lock:
        with sqlite3.connect('logs.db') as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM logs_by_levelname')
            logs = cursor.fetchall()
    return render_template('logs.html', logs=logs)

# Ruta para mostrar logs filtrados por levelname
@app.route('/logs/message')
def logs_by_message():
    with db_lock:
        with sqlite3.connect('logs.db') as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM logs_by_message')
            logs = cursor.fetchall()
    return render_template('logs.html', logs=logs)



# Corremos el servidor
if __name__ == "__main__":
    app.run(port=5000, debug=True)
