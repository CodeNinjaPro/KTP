from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
import redis
import json
from pymongo import MongoClient

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Configure Redis client
# List of Redis host configurations
REDIS_HOSTS = [
    {'host': '192.168.0.80', 'port': 6379},
    # Add more hosts as needed
]

def create_redis_client(host, port):
    return redis.StrictRedis(host=host, port=port, decode_responses=True)

# Initialize MongoDB client
MONGO_URI = 'mongodb+srv://ktpuser:s59vs6gF6Xird9ET@ktp.s2aegiz.mongodb.net/'
mongo_client = MongoClient(MONGO_URI)
db = mongo_client['sensor_data_db']
collection = db['sensor_data']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

def save_to_mongodb(data):
    result = collection.insert_one(data)
    print(f'Data saved to MongoDB with document ID: {result.inserted_id}')

def read_redis_data():
    pubsub = redis_client.pubsub()
    pubsub.subscribe('sensor_data')
    for message in pubsub.listen():
        if message['type'] == 'message':
            data = json.loads(message['data'])
            if 'error' in data:
                socketio.emit('alert', {'message': data['error']}, namespace='/', broadcast=True)
                print('error')
            else:
                socketio.emit('updateData', data, namespace='/', broadcast=True)
                save_to_mongodb(data)
                print(data)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

if __name__ == '__main__':
    # Create and start a thread for each Redis host
    threads = []
    for host_config in REDIS_HOSTS:
        redis_client = create_redis_client(host_config['host'], host_config['port'])
        data_thread = threading.Thread(target=read_redis_data, args=(redis_client,))
        data_thread.daemon = True
        data_thread.start()
        threads.append(data_thread)
        
    socketio.run(app, debug=True)
