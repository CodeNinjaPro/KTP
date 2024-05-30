from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
import redis
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Configure Redis client
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

def read_redis_data():
    pubsub = redis_client.pubsub()
    pubsub.subscribe('sensor_data')
    for message in pubsub.listen():
        if message['type'] == 'message':
            data = json.loads(message['data'])
            if 'error' in data:
                socketio.emit('alert', {'message': data['error']}, namespace='/', broadcast=True)
            else:
                socketio.emit('updateData', data, namespace='/', broadcast=True)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

if __name__ == '__main__':
    data_thread = threading.Thread(target=read_redis_data)
    data_thread.daemon = True
    data_thread.start()
    socketio.run(app, debug=True)
