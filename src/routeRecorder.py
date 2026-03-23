from vex import *

brain = Brain()
csvHeaderText = "time, left_deg, right_deg"
sd_file_name = "envRecording.csv" 
data_buffer = csvHeaderText + "\n"

# Define your motors (adjust ports and reverse flags as needed for your specific bot)
left1_motor = Motor(Ports.PORT11, False)
left2_motor = Motor(Ports.PORT12, False)
left_drive_group = MotorGroup(left1_motor, left2_motor)
right1_motor = Motor(Ports.PORT8, True)
right2_motor = Motor(Ports.PORT10, True)
right_drive_group = MotorGroup(right1_motor, right2_motor)

drivetrain = DriveTrain(left_drive_group, right_drive_group, 319.19, 295, 40, MM, 1)

def recorder(numOfDataEntries, polling_delay_msec):
    global data_buffer
    
    # Reset motor encoders to zero at the start of recording
    left_drive_group.set_position(0, DEGREES)
    right_drive_group.set_position(0, DEGREES)
    brain.timer.clear()

    for i in range(numOfDataEntries):
        data_buffer += "%1.3f," % brain.timer.value()
        data_buffer += "%1.1f," % left_drive_group.position(DEGREES)
        data_buffer += "%1.1f\n" % right_drive_group.position(DEGREES)
        wait(polling_delay_msec, MSEC)

# Run motors forward and record for 5 seconds (100 chunks of 50msec)
drivetrain.drive(FORWARD)
recorder(100, 50)
drivetrain.turn(RIGHT)
recorder(100, 50)
drivetrain.stop()

# Save logic
if not brain.sdcard.is_inserted():
    brain.screen.set_cursor(1,1)
    brain.screen.print("SD Card Missing")
    while True:
        wait(5, MSEC)
        
brain.screen.set_cursor(4,1)
if brain.sdcard.savefile(sd_file_name, bytearray(data_buffer,'utf-8')) == 0:
    brain.screen.print("SD Write Error")
else:
    brain.screen.print("Data Written")