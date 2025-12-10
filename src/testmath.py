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

