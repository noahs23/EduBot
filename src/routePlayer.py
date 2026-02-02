from vex import *
brain = Brain()
brain_inertial = Inertial(Ports.PORT16)
csvHeaderText = "time, x, y, z"
sd_file_name = "envRecording.csv" 
data_buffer = csvHeaderText + "\n"

def tempReader()