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

# Brain should be defined by default
brain=Brain()

# Robot configuration code
left1_motor = Motor(Ports.PORT11, False)
left2_motor = Motor(Ports.PORT12, False)
left_drive_group = MotorGroup(left1_motor, left2_motor)
right1_motor = Motor(Ports.PORT8, True)
right2_motor = Motor(Ports.PORT10, True)
right_drive_group = MotorGroup(right1_motor, right2_motor)

drivetrain = DriveTrain(left_drive_group, right_drive_group, 319.19, 295, 40, MM, 1)

# Begin project code

import math

def degrees_per_second_to_m_s(degrees_per_second, radius_meters):
    """
    Converts angular velocity in degrees per second to linear velocity in meters per second.

    Args:
        degrees_per_second (float): The angular velocity to convert.
        radius_meters (float): The radius of the rotation in meters.

    Returns:
        float: The linear velocity in meters per second.
    """
    # 1. Convert degrees per second to radians per second
    # There are 180 degrees in pi radians
    radians_per_second = degrees_per_second * (math.pi / 180.0)
    
    # 2. Calculate linear velocity (v = omega * r)
    # v (m/s) = omega (rad/s) * r (m)
    linear_velocity_m_s = radians_per_second * radius_meters
    
    return linear_velocity_m_s

# --- Example Usage ---
# Example: A point on a wheel rotating at 90 degrees/sec, 
# 0.5 meters from the center (radius).
velocityMS = 0.19
drivetrain.drive(FORWARD)
wait(1/velocityMS, SECONDS)
drivetrain.stop()


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
    


    