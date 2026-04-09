

import http.server
import json
import os
import queue
import threading
import time
import urllib.parse
 
SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200
PORT = 5000
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEOS_DIR = os.path.join(SCRIPT_DIR, "videos")
 
checkpoints = []
robot_status = {"state": "disconnected", "position": "HOME"}
serial_fd = None
serial_lock = threading.Lock()
video_subscribers = []
video_subscribers_lock = threading.Lock()
 
 
def configure_serial(path, baud):
    import termios
    fd = os.open(path, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    attrs = termios.tcgetattr(fd)
    baud_map = {
        9600: termios.B9600,
        19200: termios.B19200,
        38400: termios.B38400,
        57600: termios.B57600,
        115200: termios.B115200,
    }
    speed = baud_map.get(baud, termios.B115200)
    attrs[0] = 0
    attrs[1] = 0
    attrs[2] = termios.CS8 | termios.CREAD | termios.CLOCAL
    attrs[3] = 0
    attrs[4] = speed
    attrs[5] = speed
    attrs[6][termios.VMIN] = 0
    attrs[6][termios.VTIME] = 1
    termios.tcsetattr(fd, termios.TCSANOW, attrs)
    import fcntl
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags & ~os.O_NONBLOCK)
    return fd
 
 
def connect_serial():
    global serial_fd
    while True:
        try:
            serial_fd = configure_serial(SERIAL_PORT, BAUD_RATE)
            robot_status["state"] = "connecting"
            print("Serial connected on " + SERIAL_PORT)
            return
        except Exception as e:
            print("Waiting for VEX brain... (" + str(e) + ")")
            time.sleep(2)
 
 
def serial_write(msg):
    with serial_lock:
        if serial_fd is not None:
            try:
                os.write(serial_fd, (msg + "\n").encode("utf-8"))
                return True
            except:
                pass
    return False
 
 
def serial_reader_thread():
    global checkpoints
    buf = b""
    while True:
        if serial_fd is None:
            time.sleep(1)
            continue
        try:
            chunk = os.read(serial_fd, 256)
            if not chunk:
                time.sleep(0.05)
                continue
            buf += chunk
            while b"\n" in buf:
                line_bytes, buf = buf.split(b"\n", 1)
                line = line_bytes.decode("utf-8", errors="ignore").strip()
                if not line:
                    continue
                handle_serial_line(line)
        except OSError:
            time.sleep(0.1)
 
 
def handle_serial_line(line):
    global checkpoints
    if line.startswith("READY:"):
        names = line[6:].split(",")
        checkpoints = [n.strip() for n in names if n.strip()]
        robot_status["state"] = "ready"
        robot_status["position"] = "HOME"
        print("Checkpoints: " + str(checkpoints))
 
    elif line.startswith("MOVING:"):
        robot_status["state"] = "moving"
        print("Moving to " + line[7:])
 
    elif line.startswith("ARRIVED:"):
        target = line[8:]
        robot_status["state"] = "ready"
        robot_status["position"] = target
        print("Arrived at " + target)
        notify_video_subscribers(target)
 
    elif line.startswith("ERR:"):
        robot_status["state"] = "ready"
        print("Error: " + line[4:])
 
 
def notify_video_subscribers(checkpoint):
    with video_subscribers_lock:
        dead = []
        for q in video_subscribers:
            try:
                q.put_nowait(checkpoint)
            except:
                dead.append(q)
        for q in dead:
            video_subscribers.remove(q)
 
 
def get_video_map():
    mapping = {}
    if not os.path.isdir(VIDEOS_DIR):
        return mapping
    for fname in os.listdir(VIDEOS_DIR):
        name, ext = os.path.splitext(fname)
        if ext.lower() in (".mp4", ".webm", ".mov", ".m4v"):
            mapping[name] = "/videos/" + fname
    return mapping
 
 
def serve_file(handler, filepath, content_type=None):
    if not os.path.isfile(filepath):
        handler.send_response(404)
        handler.end_headers()
        return
    if content_type is None:
        ext = os.path.splitext(filepath)[1].lower()
        types = {
            ".html": "text/html",
            ".js": "application/javascript",
            ".css": "text/css",
            ".json": "application/json",
            ".mp4": "video/mp4",
            ".webm": "video/webm",
            ".mov": "video/quicktime",
            ".m4v": "video/mp4",
        }
        content_type = types.get(ext, "application/octet-stream")
 
    size = os.path.getsize(filepath)
    range_header = handler.headers.get("Range")
 
    if range_header and content_type.startswith("video/"):
        start, end = 0, size - 1
        range_spec = range_header.replace("bytes=", "")
        parts = range_spec.split("-")
        start = int(parts[0]) if parts[0] else 0
        end = int(parts[1]) if len(parts) > 1 and parts[1] else size - 1
        length = end - start + 1
 
        handler.send_response(206)
        handler.send_header("Content-Type", content_type)
        handler.send_header("Content-Length", str(length))
        handler.send_header("Content-Range", "bytes " + str(start) + "-" + str(end) + "/" + str(size))
        handler.send_header("Accept-Ranges", "bytes")
        handler.end_headers()
 
        with open(filepath, "rb") as f:
            f.seek(start)
            remaining = length
            while remaining > 0:
                chunk = f.read(min(65536, remaining))
                if not chunk:
                    break
                handler.wfile.write(chunk)
                remaining -= len(chunk)
    else:
        handler.send_response(200)
        handler.send_header("Content-Type", content_type)
        handler.send_header("Content-Length", str(size))
        if content_type.startswith("video/"):
            handler.send_header("Accept-Ranges", "bytes")
        handler.end_headers()
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(65536)
                if not chunk:
                    break
                handler.wfile.write(chunk)
 
 
def send_json(handler, data, status=200):
    body = json.dumps(data).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)
 
 
class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass
 
    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
 
        if path == "/":
            serve_file(self, os.path.join(SCRIPT_DIR, "checkpointController.html"))
 
        elif path == "/display":
            serve_file(self, os.path.join(SCRIPT_DIR, "videoPlayer.html"))
 
        elif path == "/api/status":
            send_json(self, {
                "checkpoints": checkpoints,
                "state": robot_status["state"],
                "position": robot_status["position"]
            })
 
        elif path == "/api/videos":
            send_json(self, {"videos": get_video_map()})
 
        elif path == "/api/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()
 
            q = queue.Queue()
            with video_subscribers_lock:
                video_subscribers.append(q)
            try:
                self.wfile.write(("data: " + json.dumps({"type": "connected"}) + "\n\n").encode())
                self.wfile.flush()
                while True:
                    try:
                        cp = q.get(timeout=15)
                        self.wfile.write(("data: " + json.dumps({"type": "arrived", "checkpoint": cp}) + "\n\n").encode())
                        self.wfile.flush()
                    except queue.Empty:
                        self.wfile.write(": keepalive\n\n".encode())
                        self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
            finally:
                with video_subscribers_lock:
                    if q in video_subscribers:
                        video_subscribers.remove(q)
 
        elif path.startswith("/videos/"):
            filename = path[8:]
            filepath = os.path.join(VIDEOS_DIR, filename)
            if ".." in filename or filename.startswith("/"):
                self.send_response(403)
                self.end_headers()
            else:
                serve_file(self, filepath)
 
        else:
            self.send_response(404)
            self.end_headers()
 
    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else b""
 
        if path == "/api/goto":
            try:
                data = json.loads(body)
            except:
                send_json(self, {"ok": False, "error": "bad json"}, 400)
                return
            target = data.get("checkpoint", "")
            if not target:
                send_json(self, {"ok": False, "error": "no checkpoint specified"}, 400)
                return
            if robot_status["state"] == "moving":
                send_json(self, {"ok": False, "error": "robot is already moving"}, 409)
                return
            ok = serial_write("GOTO:" + target)
            send_json(self, {"ok": ok})
 
        elif path == "/api/home":
            if robot_status["state"] == "moving":
                send_json(self, {"ok": False, "error": "robot is already moving"}, 409)
                return
            ok = serial_write("HOME")
            send_json(self, {"ok": ok})
 
        else:
            self.send_response(404)
            self.end_headers()
 
 
class ThreadedServer(http.server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True
 
    def process_request(self, request, client_address):
        t = threading.Thread(target=self.process_request_thread, args=(request, client_address))
        t.daemon = True
        t.start()
 
    def process_request_thread(self, request, client_address):
        try:
            self.finish_request(request, client_address)
        except Exception:
            self.handle_error(request, client_address)
        finally:
            self.shutdown_request(request)
 
 
if __name__ == "__main__":
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    connect_serial()
 
    reader = threading.Thread(target=serial_reader_thread, daemon=True)
    reader.start()
 
    server = ThreadedServer(("0.0.0.0", PORT), Handler)
    print("Starting server on http://0.0.0.0:" + str(PORT))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down")
        server.shutdown()

