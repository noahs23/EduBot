# ----------------------------------------------------------------------------- #
#                                                                               #             
# 	Project:        Drivetrain Sensing                                          #
#   Module:         main.py                                                     #
#   Author:         VEX                                                         #
#   Created:        Fri Aug 05 2022                                             #
#	Description:    This example will show all of the available commands        #
#                   for using the Drivetrain                                    #
#                                                                               #                                                                          
#   Configuration:  V5 Speedbot (Drivetrain 2-motor, No Gyro)                   #
#                                                                               #                                                                          
# ----------------------------------------------------------------------------- #

# Library imports
from vex import *

brain.screen.clear_screen()
brain.screen.set_cursor(1, 1)
brain.screen.print("Loading route...")
 
data = load_recording(sd_file_name)
cumulative = compute_cumulative_distances(data)
cp_table = build_checkpoint_table(data, cumulative)
 
cp_names = sorted(cp_table.keys())
current_inches = 0.0
 
brain.screen.clear_screen()
brain.screen.set_cursor(1, 1)
brain.screen.print("Ready - " + str(len(cp_names)) + " CPs")
brain.screen.next_row()
brain.screen.print("Waiting for command...")
 
send_serial("READY:" + ",".join(cp_names))
 
while True:
    line = read_serial_line()
    if line is None:
        wait(20, MSEC)
        continue
 
    if line.startswith("GOTO:"):
        target = line[5:].strip()
 
        if target not in cp_table:
            send_serial("ERR:unknown checkpoint")
            brain.screen.set_cursor(3, 1)
            brain.screen.clear_row()
            brain.screen.print("Unknown: " + target)
            continue
 
        target_inches = cp_table[target]
        delta = target_inches - current_inches
 
        brain.screen.set_cursor(2, 1)
        brain.screen.clear_row()
        brain.screen.print("-> " + target)
        brain.screen.set_cursor(3, 1)
        brain.screen.clear_row()
        brain.screen.print("Dist: " + "%1.1f" % delta + " in")
 
        send_serial("MOVING:" + target)
        drive_inches(delta)
        current_inches = target_inches
 
        send_serial("ARRIVED:" + target)
        brain.screen.set_cursor(4, 1)
        brain.screen.clear_row()
        brain.screen.print("At: " + target)
 
    elif line == "HOME":
        delta = -current_inches
        brain.screen.set_cursor(2, 1)
        brain.screen.clear_row()
        brain.screen.print("-> HOME")
 
        send_serial("MOVING:HOME")
        drive_inches(delta)
        current_inches = 0.0
 
        send_serial("ARRIVED:HOME")
        brain.screen.set_cursor(4, 1)
        brain.screen.clear_row()
        brain.screen.print("At: HOME")
 
    elif line == "PING":
        send_serial("PONG")
 
    wait(20, MSEC)
 

# Print all Drivetrain sensing values to the screen in an infinite loop
while True:
    # Clear the screen and set the cursor to top left corner on each loop
    velocity = degrees_per_second_to_m_s(drivetrain.velocity(VelocityUnits.DPS), 0.034925)
    brain.screen.clear_screen()
    brain.screen.set_cursor(1,1)

    brain.screen.print("Velocity:", velocity)
    brain.screen.next_row()

    brain.screen.print("Current:", drivetrain.current(CurrentUnits.AMP))
    brain.screen.next_row()

    brain.screen.print("Power:", drivetrain.power(PowerUnits.WATT))
    brain.screen.next_row()

    brain.screen.print("Torque:", drivetrain.torque(TorqueUnits.NM))
    brain.screen.next_row()

    brain.screen.print("Efficiency:", drivetrain.efficiency(PERCENT))
    brain.screen.next_row()

    # brain.screen.print("Temperature:", drivetrain.temperature(PERCENT)) # type: ignore
    # brain.screen.next_row()

    # A brief delay to allow text to be printed without distortion or tearing
    wait(100,MSEC)
    


    