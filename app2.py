from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
import random
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

def random_data():
    while True:
        time.sleep(2)
        data = {
            'temperature': random.uniform(20, 30),
            'humidity': random.uniform(40, 60),
            'vwc': random.uniform(10, 30),
        }
        socketio.emit('updateData', data, namespace='/', broadcast=True)

        if random.choice([True, False]):
            socketio.emit('alert', {'message': 'Anomaly detected!'}, namespace='/', broadcast=True)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

if __name__ == '__main__':
    data_thread = threading.Thread(target=random_data)
    data_thread.daemon = True
    data_thread.start()
    socketio.run(app, debug=True)
