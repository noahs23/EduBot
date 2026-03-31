import serial
import threading
import json
import time
from flask import Flask, send_file, jsonify, request

SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200

app = Flask(__name__)

ser = None
lock = threading.Lock()
checkpoints = []
robot_status = {"state": "disconnected", "position": "HOME"}
status_log = []

def connect_serial():
    global ser
    while True:
        try:
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
            robot_status["state"] = "connecting"
            print("Serial connected on " + SERIAL_PORT)
            return
        except Exception as e:
            print("Waiting for VEX brain... (" + str(e) + ")")
            time.sleep(2)

def serial_reader():
    global checkpoints
    while True:
        if ser is None or not ser.is_open:
            time.sleep(1)
            continue
        try:
            line = ser.readline().decode("utf-8").strip()
            if not line:
                continue

            status_log.append({"time": time.time(), "msg": line})
            if len(status_log) > 100:
                status_log.pop(0)

            if line.startswith("READY:"):
                names = line[6:].split(",")
                checkpoints = [n.strip() for n in names if n.strip()]
                robot_status["state"] = "ready"
                robot_status["position"] = "HOME"
                print("Checkpoints: " + str(checkpoints))

            elif line.startswith("MOVING:"):
                target = line[7:]
                robot_status["state"] = "moving"
                print("Moving to " + target)

            elif line.startswith("ARRIVED:"):
                target = line[8:]
                robot_status["state"] = "ready"
                robot_status["position"] = target
                print("Arrived at " + target)

            elif line.startswith("ERR:"):
                robot_status["state"] = "ready"
                print("Error: " + line[4:])

        except Exception as e:
            print("Serial read error: " + str(e))
            time.sleep(0.5)

def send_command(cmd):
    with lock:
        if ser and ser.is_open:
            ser.write((cmd + "\n").encode("utf-8"))
            return True
    return False

@app.route("/")
def index():
    return send_file("checkpointController.html")

@app.route("/api/status")
def api_status():
    return jsonify({
        "checkpoints": checkpoints,
        "state": robot_status["state"],
        "position": robot_status["position"]
    })

@app.route("/api/goto", methods=["POST"])
def api_goto():
    body = request.get_json()
    target = body.get("checkpoint", "")
    if not target:
        return jsonify({"ok": False, "error": "no checkpoint specified"}), 400
    if robot_status["state"] == "moving":
        return jsonify({"ok": False, "error": "robot is already moving"}), 409
    ok = send_command("GOTO:" + target)
    return jsonify({"ok": ok})

@app.route("/api/home", methods=["POST"])
def api_home():
    if robot_status["state"] == "moving":
        return jsonify({"ok": False, "error": "robot is already moving"}), 409
    ok = send_command("HOME")
    return jsonify({"ok": ok})

if __name__ == "__main__":
    connect_serial()
    reader_thread = threading.Thread(target=serial_reader, daemon=True)
    reader_thread.start()
    print("Starting server on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
