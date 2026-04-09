from vex import *
import math
import csv


class GenericSerial:
    def __init__(self, port, baud_rate):
        self.port = port
        self.baud_rate = baud_rate
        self.buffer = bytearray()

    def available(self):
        return len(self.buffer)

    def read(self, n):
        data = self.buffer[:n]
        self.buffer = self.buffer[n:]
        return data

    def write(self, data):
        pass  # Mock: no actual output


brain = Brain()
brain_inertial = Inertial(Ports.PORT16)

left1_motor = Motor(Ports.PORT11, False)
left2_motor = Motor(Ports.PORT12, False)
left_drive_group = MotorGroup(left1_motor, left2_motor)
right1_motor = Motor(Ports.PORT8, True)
right2_motor = Motor(Ports.PORT10, True)
right_drive_group = MotorGroup(right1_motor, right2_motor)

serial_port = GenericSerial(Ports.PORT1, 115200)
 
sd_file_name = "envRecording_merged.csv"
 
# ── PID ────────────────────────────────
 
class PID:
    def __init__(self, kP, kI, kD, integral_limit=0, output_limit=100):
        self.kP = kP
        self.kI = kI
        self.kD = kD
        self.integral_limit = integral_limit
        self.output_limit = output_limit
        self.integral = 0.0
        self.last_error = 0.0
        self.first = True
 
    def reset(self):
        self.integral = 0.0
        self.last_error = 0.0
        self.first = True
 
    def step(self, error, dt):
        if self.first:
            self.last_error = error
            self.first = False
        self.integral += error * dt
        if self.integral_limit:
            if self.integral > self.integral_limit:
                self.integral = self.integral_limit
            if self.integral < -self.integral_limit:
                self.integral = -self.integral_limit
        derivative = (error - self.last_error) / dt if dt > 0 else 0.0
        self.last_error = error
        out = self.kP * error + self.kI * self.integral + self.kD * derivative
        if out > self.output_limit:
            out = self.output_limit
        if out < -self.output_limit:
            out = -self.output_limit
        return out
 
 
def inches_to_degrees(inches, wheel_diameter_in=4.0):
    return (inches / (math.pi * wheel_diameter_in)) * 360.0
 
 
def avg_deg():
    return (left_drive_group.position(DEGREES) + right_drive_group.position(DEGREES)) / 2.0
 
 
def drive_inches(inches, max_power=80, timeout=5.0):
    target_deg = inches_to_degrees(inches)
    pid = PID(0.35, 0.0, 1.2, integral_limit=200, output_limit=max_power)
 
    left_drive_group.set_position(0, DEGREES)
    right_drive_group.set_position(0, DEGREES)
 
    total = Timer()
    total.reset()
    step_timer = Timer()
    step_timer.reset()
    settled_start = None
 
    while total.time(SECONDS) < timeout:
        dt = step_timer.time(SECONDS)
        step_timer.reset()
        error = target_deg - avg_deg()
        power = pid.step(error, dt)
        left_drive_group.spin(FORWARD, power, PERCENT)
        right_drive_group.spin(FORWARD, power, PERCENT)
        if abs(error) <= 5:
            if settled_start is None:
                settled_start = total.time(SECONDS)
            elif total.time(SECONDS) - settled_start >= 0.20:
                break
        else:
            settled_start = None
        wait(10, MSEC)
 
    left_drive_group.stop(BRAKE)
    right_drive_group.stop(BRAKE)
 
# ── CSV loading & distance precomputation ─────────────────────────────────────
 
def load_recording(file_name):
    data = {}
    with open(file_name, "r") as f:
        reader = csv.reader(f)
        headers = [h.strip() for h in next(reader)]
        for h in headers:
            data[h] = []
        for row in reader:
            for h, val in zip(headers, row):
                val = val.strip()
                if h == "checkpoint":
                    data[h].append(val)
                else:
                    data[h].append(float(val))
    return data
 
 
def compute_cumulative_distances(data):
    distances = [0.0]
    vx, vy, vz = 0.0, 0.0, 0.0
 
    for i in range(1, len(data["time"])):
        dt = data["time"][i] - data["time"][i - 1]
        ax = (data["x"][i] + data["x"][i - 1]) / 2.0
        ay = (data["y"][i] + data["y"][i - 1]) / 2.0
        az = (data["z"][i] + data["z"][i - 1]) / 2.0
        vx += ax * dt
        vy += ay * dt
        vz += az * dt
        dx = vx * dt
        dy = vy * dt
        dz = vz * dt
        step = math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
        distances.append(distances[-1] + step)
 
    m_to_in = 39.3701
    return [d * m_to_in for d in distances]
 
 
def build_checkpoint_table(data, cumulative_inches):
    table = {}
    for i, label in enumerate(data["checkpoint"]):
        if label:
            table[label] = cumulative_inches[i]
    return table
 
# ── Serial helpers ────────────────────────────────────────────────────────────
 
rx_buffer = ""
 
def read_serial_line():
    global rx_buffer
    n = serial_port.available()
    if n > 0:
        raw = serial_port.read(n)
        rx_buffer += "".join(chr(b) for b in raw)
    idx = rx_buffer.find("\n")
    if idx >= 0:
        line = rx_buffer[:idx].strip()
        rx_buffer = rx_buffer[idx + 1:]
        return line
    return None


def send_serial(msg):
    serial_port.write(bytearray(msg + "\n", "utf-8"))