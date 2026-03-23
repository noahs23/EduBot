from vex import *

brain = Brain()
sd_file_name = "envRecording.csv"

# Define the motors exactly as they are in the recorder
left1_motor = Motor(Ports.PORT11, False)
left2_motor = Motor(Ports.PORT12, False)
left_drive_group = MotorGroup(left1_motor, left2_motor)

right1_motor = Motor(Ports.PORT8, True)
right2_motor = Motor(Ports.PORT10, True)
right_drive_group = MotorGroup(right1_motor, right2_motor)

def read_csv_as_dict(file_name):
    """Reads a CSV file and returns a dict of lists, no imports needed."""
    data = {}
    with open(file_name, "r") as f:
        lines = f.read().strip().split("\n")
        headers = [h.strip() for h in lines[0].split(",")]
        for h in headers:
            data[h] = []
        for line in lines[1:]:
            values = line.split(",")
            for h, val in zip(headers, values):
                data[h].append(float(val.strip()))
    return data

def play_route_totals(sd_file_name):
    """
    Reads the CSV, finds the total recorded degrees for left and right,
    and commands the motors to spin that total amount.
    """
    df = read_csv_as_dict(sd_file_name)

    # Get the very last recorded position (total degrees traveled)
    total_left_deg = df["left_deg"][-1]
    total_right_deg = df["right_deg"][-1]

    brain.screen.clear_screen()
    brain.screen.set_cursor(1, 1)
    brain.screen.print("Left Target: ", total_left_deg)
    brain.screen.set_cursor(2, 1)
    brain.screen.print("Right Target: ", total_right_deg)

    # Set both to spin. 'wait=False' on the first one ensures they spin at the same time
    left_drive_group.spin_for(FORWARD, total_left_deg, DEGREES, wait=False)
    right_drive_group.spin_for(FORWARD, total_right_deg, DEGREES, wait=True)
    
    brain.screen.set_cursor(4, 1)
    brain.screen.print("Playback Complete")

# Execute playback
play_route_totals(sd_file_name)