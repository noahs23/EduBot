from vex import *
brain = Brain()
brain_inertial = Inertial(Ports.PORT16)
csvHeaderText = "time, x, y, z"
sd_file_name = "envRecording.csv"

import csv
import math

def read_csv_as_dict(file_name):
    """Reads a CSV file and returns a dict of lists, similar to a DataFrame."""
    data = {}
    with open(file_name, "r") as f:
        reader = csv.reader(f)
        headers = [h.strip() for h in next(reader)]
        for h in headers:
            data[h] = []
        for row in reader:
            for h, val in zip(headers, row):
                data[h].append(float(val.strip()))
    return data

def total_inches_traveled(sd_file_name):
    """
    Reads a CSV with columns: time, x, y, z (accelerations in m/s^2)
    and computes total inches traveled by integrating acceleration -> velocity -> distance.
    """
    df = read_csv_as_dict(sd_file_name)

    velocity_x = 0.0
    velocity_y = 0.0
    velocity_z = 0.0
    total_distance_m = 0.0

    for i in range(1, len(df["time"])):
        dt = df["time"][i] - df["time"][i - 1]

        # Average acceleration over the interval (trapezoidal integration)
        avg_ax = (df["x"][i] + df["x"][i - 1]) / 2.0
        avg_ay = (df["y"][i] + df["y"][i - 1]) / 2.0
        avg_az = (df["z"][i] + df["z"][i - 1]) / 2.0

        # Update velocities
        velocity_x += avg_ax * dt
        velocity_y += avg_ay * dt
        velocity_z += avg_az * dt

        # Displacement in this interval
        dx = velocity_x * dt
        dy = velocity_y * dt
        dz = velocity_z * dt

        # Euclidean distance for this time step
        step_distance = math.sqrt(dx**2 + dy**2 + dz**2)
        total_distance_m += step_distance

    # Convert meters to inches
    total_inches = total_distance_m * 39.3701
    return total_inches