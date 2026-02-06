from vex import *
brain = Brain()
brain_inertial = Inertial(Ports.PORT16)
csvHeaderText = "time, x, y, z"
sd_file_name = "envRecording.csv" 
data_buffer = csvHeaderText + "\n"
        
def recorder(numOfDataEntries, polling_delay_msec):
    for i in range(numOfDataEntries):
        global data_buffer
        data_buffer += "%1.3f" % brain.timer.value() + ","
        data_buffer += "%1.3f" % brain_inertial.acceleration(XAXIS) + ","
        data_buffer += "%1.3f" % brain_inertial.acceleration(YAXIS) + ","
        data_buffer += "%1.3f" % brain_inertial.acceleration(ZAXIS) + "\n"
        wait(polling_delay_msec)
        # brain.screen.print(data_buffer)
        # with open("data_buffer.csv", "a") as f:
        #      f.write(data_buffer)
        # wait(polling_delay_msec)
        # brain.screen.new_line()
        # if (brain.screen.row() == 12):
        #     brain.screen.set_cursor(1, 1)
        #     brain.screen.clear_screen()
        
recorder(20, 1000)

if not brain.sdcard.is_inserted():
    brain.screen.set_cursor(1,1)
    brain.screen.print("SD Card Missing")
    while(True):
        wait(5, MSEC)
        
brain.screen.set_cursor(4,1)
if brain.sdcard.savefile(sd_file_name, bytearray(data_buffer,'utf-8')) == 0:
    brain.screen.print("SD Write Error")
else:
    brain.screen.print("Data Written")