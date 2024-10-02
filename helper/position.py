import cv2
from numpy.f2py.auxfuncs import throw_error

def calc_turn(ball, image_width=1280, fov=90):
    robot_x = image_width // 2

    center = cv2.moments(ball)
    if center["m00"] == 0:
        throw_error(center)

    ball_x = int(center["m10"] / center["m00"])
    pixel_offset_x = ball_x - robot_x
    pixels_per_degree = image_width / fov

    return pixel_offset_x / pixels_per_degree