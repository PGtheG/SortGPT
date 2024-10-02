from helper.position import calc_turn
from modules.camera import handle_color_in_gripper


def handle_moving(robot, ball, frame):
    degree = calc_turn(ball)
    if degree > 1 or degree < -1:
        turn(robot, degree)

    processed_frame= drive_to_ball(robot, frame)

    return processed_frame

def move_forward(robot, length, speed=1.0):
    chassis = robot.chassis
    chassis.move(x=length, xy_speed=speed).wait_for_completed()

def move_backwards(robot, length, speed):
    chassis = robot.chassis
    length = length * -1
    chassis.move(x=length, xy_speed=speed).wait_for_completed()

def move_right(robot, length, speed):
    chassis = robot.chassis
    chassis.move(y=length, xy_speed=speed).wait_for_completed()

def move_left(robot, length, speed):
    chassis = robot.chassis
    length = length * -1
    chassis.move(y=length, xy_speed=speed).wait_for_completed()

def turn(robot, degree, speed=100):
    chassis = robot.chassis
    degree = degree * -1
    chassis.move(z=degree, z_speed=speed).wait_for_completed()

def drive_to_ball(robot, frame):
    color_not_in_gripper, processed_frame = handle_color_in_gripper(frame)
    if color_not_in_gripper:
        move_forward(robot, 0.1, 0.5)

    return processed_frame