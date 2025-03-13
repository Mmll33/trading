from flask import Flask, jsonify
import Trading_bot_XAU_USDT as bot
from threading import Thread
import time

app = Flask(__name__)

# Variable global para almacenar los datos del bot
latest_data = {}

@app.route('/')
def get_status():
    return jsonify({'message': 'status: Bot en ejecución!'})

@app.route('/data')
def get_data():
    return jsonify(latest_data)

def bot_loop():
    global latest_data
    while True:
        latest_data = bot.run_bot()  # Actualiza la variable con nuevos datos
        time.sleep(60)  # Espera 60 segundos antes de la siguiente ejecución

if __name__ == '__main__':
    # Hilo para ejecutar Flask
    flask_thread = Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False))
    flask_thread.start()

    # Hilo para el bot de trading
    bot_thread = Thread(target=bot_loop)
    bot_thread.start()
