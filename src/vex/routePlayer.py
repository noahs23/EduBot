from vex import *

brain = Brain()
brain_inertial = Inertial(Ports.PORT16)
csvHeaderText = "time,x,y,z,checkpoint"
sd_file_name = "envRecording_merged.csv"

import csv
import math


def read_csv_as_dict(file_name):
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


def list_checkpoints(data):
    result = []
    for i, label in enumerate(data["checkpoint"]):
        if label:
            result.append((i, label))
    return result


def checkpoint_index(data, label):
    for i, cp in enumerate(data["checkpoint"]):
        if cp == label:
            return i
    return -1


def slice_to_checkpoint(data, label):
    idx = checkpoint_index(data, label)
    if idx == -1:
        return None
    sliced = {}
    for key in data:
        sliced[key] = data[key][: idx + 1]
    return sliced


def slice_between_checkpoints(data, start_label, end_label):
    if start_label:
        s = checkpoint_index(data, start_label)
        if s == -1:
            return None
    else:
        s = 0
    if end_label:
        e = checkpoint_index(data, end_label)
        if e == -1:
            return None
    else:
        e = len(data["time"]) - 1
    sliced = {}
    for key in data:
        sliced[key] = data[key][s: e + 1]
    return sliced


def _compute_inches(data):
    velocity_x = 0.0
    velocity_y = 0.0
    velocity_z = 0.0
    total_distance_m = 0.0

    for i in range(1, len(data["time"])):
        dt = data["time"][i] - data["time"][i - 1]

        avg_ax = (data["x"][i] + data["x"][i - 1]) / 2.0
        avg_ay = (data["y"][i] + data["y"][i - 1]) / 2.0
        avg_az = (data["z"][i] + data["z"][i - 1]) / 2.0

        velocity_x += avg_ax * dt
        velocity_y += avg_ay * dt
        velocity_z += avg_az * dt

        dx = velocity_x * dt
        dy = velocity_y * dt
        dz = velocity_z * dt

        step_distance = math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
        total_distance_m += step_distance

    return total_distance_m * 39.3701


def total_inches_traveled(sd_file_name):
    df = read_csv_as_dict(sd_file_name)
    return _compute_inches(df)


def inches_to_checkpoint(sd_file_name, label):
    df = read_csv_as_dict(sd_file_name)
    segment = slice_to_checkpoint(df, label)
    if segment is None:
        return -1
    return _compute_inches(segment)


def inches_between_checkpoints(sd_file_name, start_label, end_label):
    df = read_csv_as_dict(sd_file_name)
    segment = slice_between_checkpoints(df, start_label, end_label)
    if segment is None:
        return -1
    return _compute_inches(segment)


def print_checkpoint_summary(sd_file_name):
    df = read_csv_as_dict(sd_file_name)
    cps = list_checkpoints(df)

    brain.screen.clear_screen()
    brain.screen.set_cursor(1, 1)

    if not cps:
        brain.screen.print("No checkpoints found")
        return

    brain.screen.print("Checkpoints:")
    brain.screen.next_row()

    for idx, label in cps:
        segment = slice_to_checkpoint(df, label)
        dist = _compute_inches(segment)
        brain.screen.print(label + ": " + "%1.2f" % dist + " in")
        brain.screen.next_row()
