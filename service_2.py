from flask import Flask, render_template, request, redirect
from logging.handlers import HTTPHandler
from datetime import datetime
import sqlite3
import logging
import threading
import time
import requests

# Configura la aplicación Flask
app = Flask(__name__)



# Configura el logger
logger = logging.getLogger('service_logger')
logger.setLevel(logging.INFO)

# API Key para todos los servicios
API_KEY = 'fc15c9c6-c08e-4cb5-b84b-c81f8eb4d876'

class SimpleHTTPHandler(HTTPHandler):
    def emit(self, record):
        # Extrae los campos del registro de log
        timestamp = datetime.now().isoformat()
        name = record.name
        levelname = record.levelname
        message = record.getMessage()  # Solo obtiene el mensaje sin formato
        
        # Construye el JSON con los campos separados
        log_entry = {
            'timestamp': timestamp,
            'name': name,
            'levelname': levelname,
            'message': message
        }
        
        headers = {'Authorization': f'Bearer {API_KEY}'}
        requests.post('http://localhost:5000/log', json=log_entry, headers=headers)


http_handler = SimpleHTTPHandler(
    'localhost:5000',  # URL del servidor central
    '/log',  # Endpoint del servidor para recibir logs
    method='POST'
)
logger.addHandler(http_handler)


# Ruta para redirigir la raíz a /service2
@app.route('/')
def root_redirect():
    return redirect('/service2')


@app.route('/service2', methods=['POST', 'GET'])
def service2_index():
    if request.method == 'POST':
        try:
            task_content = request.form['content']

            # Conectar a la base de datos y agregar la nueva tarea
            with sqlite3.connect('services.db') as con:
                cursor = con.cursor()
                cursor.execute(
                    "INSERT INTO service2 (content) VALUES (?)",
                    (task_content,)
                )
                con.commit()

            return redirect('/service2')
        except Exception as e:
            logger.error(f"Error: {e}")
            return 'There was an issue with your task'
    
    return render_template('index_service2.html')



# Función para generar logs
def generate_logs():
    while True:
        try:
            logger.info('Service 2: all good for now')
            time.sleep(50)
        except Exception as error:
            logger.error(f"An error occurred: {error}")



# Corremos el servicio
if __name__ == "__main__":
    # Inicia el hilo para generar logs
    log_thread = threading.Thread(target=generate_logs)
    log_thread.start()
    
    # Inicia la aplicación Flask en el puerto 5002
    app.run(port=5002, debug=True)
