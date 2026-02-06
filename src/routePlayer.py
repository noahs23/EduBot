from vex import *
import pandas as pd
brain = Brain()
brain_inertial = Inertial(Ports.PORT16)
csvHeaderText = "time, x, y, z"
sd_file_name = "envRecording.csv"

def tempReader(sd_file_name)
    sd_file = pd.read_csv(sd_file_name)
     
def acc_to_inches(accel_mpss, time_s, v0_mps=0):

    distance_m = (v0_mps * time_s) + (0.5 * accel_mpss * (time_s ** 2))
    meters_to_inches = 39.3701
    distance_inches = distance_m * meters_to_inches
    
    return distance_inches

# print(f"Acceleration: {acceleration} m/s^2")
# print(f"Time: {time} seconds")
# print(f"Distance traveled: {inches:.2f} inches")
