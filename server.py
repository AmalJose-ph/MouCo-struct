from flask import Flask, Response, request, jsonify, send_from_directory
import json, queue
from config import THRESHOLD
import webbrowser

client_queues = []
listening = False
threshold = THRESHOLD

app = Flask(__name__, static_folder="static")

def send_event(event, data):
    for q in list(client_queues):
        try:
            q.put((event, data))
        except:
            pass

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/stream")
def stream():
    def gen():
        q = queue.Queue()
        client_queues.append(q)
        q.put(('threshold', {'threshold': threshold}))
        q.put(('status', {'status': 'Listening 🎧' if listening else 'Stopped ⛔'}))
        try:
            while True:
                event, data = q.get()
                yield f"event: {event}\n"
                yield f"data: {json.dumps(data)}\n\n"
        except GeneratorExit:
            pass
        finally:
            if q in client_queues:
                client_queues.remove(q)
    return Response(gen(), mimetype='text/event-stream')

@app.route("/start", methods=["POST"])
def start_listening():
    from sound_handler import start_listening
    start_listening()
    return jsonify({"status": "ok"})

@app.route("/stop", methods=["POST"])
def stop_listening():
    from sound_handler import stop_listening
    stop_listening()
    return jsonify({"status": "ok"})

@app.route("/set_threshold", methods=["POST"])
def set_threshold():
    global threshold
    data = request.get_json(force=True)
    threshold = float(data.get("value", threshold))
    send_event("threshold", {"threshold": threshold})
    return jsonify({"status": "ok", "threshold": threshold})

def run_server():
    webbrowser.open("http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, threaded=True)
