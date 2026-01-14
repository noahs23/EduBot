from vex import *
brain = Brain()
brain_inertial = Inertial(Ports.PORT16)
        
def recorder(numOfDataEntries, polling_delay_msec):

    for i in range(numOfDataEntries):
        data_buffer = ""
        data_buffer += "%1.3f" % brain.timer.value() + ", "
        data_buffer += "%1.3f" % brain_inertial.acceleration(XAXIS) + ", " + "\n"
        brain.screen.print(data_buffer)
        wait(polling_delay_msec)
        brain.screen.new_line()
        if (brain.screen.row() == 12):
            brain.screen.set_cursor(1, 1)
            brain.screen.clear_screen()
            

recorder(100, 500)