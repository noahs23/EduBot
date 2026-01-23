import math
import main
from vex import *
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
            if self.integral > self.integral_limit: self.integral = self.integral_limit
            if self.integral < -self.integral_limit: self.integral = -self.integral_limit

        derivative = (error - self.last_error) / dt if dt > 0 else 0.0
        self.last_error = error

        out = self.kP * error + self.kI * self.integral + self.kD * derivative

        if out > self.output_limit: out = self.output_limit
        if out < -self.output_limit: out = -self.output_limit
        return out


def inches_to_degrees(inches, wheel_diameter_in):
    # wheel circumference = pi * D
    # rotations = distance / circumference
    # degrees = rotations * 360
    return (inches / (math.pi * wheel_diameter_in)) * 360.0


def avg_deg(left_drive_group, right_drive_group):
    return (left_drive_group.position(DEGREES) + right_drive_group.position(DEGREES)) / 2.0


def drive_distance(left_drive_group, right_drive_group,
                   inches, wheel_diameter_in=4.0,
                   kP=0.35, kI=0.0, kD=1.2,
                   settle_error_deg=5, settle_time=0.20,
                   timeout=3.0,
                   max_power=80):
    target_deg = inches_to_degrees(inches, wheel_diameter_in)

    pid = PID(kP, kI, kD, integral_limit=200, output_limit=max_power)

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

        error = target_deg - avg_deg(left_drive_group, right_drive_group)
        power = pid.step(error, dt)

        left_drive_group.spin(FORWARD, power, PERCENT)
        right_drive_group.spin(FORWARD, power, PERCENT)

        if abs(error) <= settle_error_deg:
            if settled_start is None:
                settled_start = total.time(SECONDS)
            elif total.time(SECONDS) - settled_start >= settle_time:
                break
        else:
            settled_start = None

        wait(10, MSEC)

    left_drive_group.stop(BRAKE)
    right_drive_group.stop(BRAKE)



