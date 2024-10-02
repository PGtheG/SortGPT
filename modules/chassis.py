from helper.position import calc_turn
from modules import camera as mod_camera


def handle_moving(robot, ball, robot_camera):
    degree = calc_turn(ball)
    if degree > 2 or degree < -2:
        turn(robot, degree, 50)

    processed_frame, has_ball_in_gripper_range, color_of_ball = drive_to_ball(robot, robot_camera)

    return processed_frame, has_ball_in_gripper_range, color_of_ball

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

def drive_to_ball(robot, robot_camera):
    has_ball_in_gripper_range, processed_frame, color_of_ball = mod_camera.handle_color_in_gripper(robot_camera)
    if has_ball_in_gripper_range is False:
        move_forward(robot, 0.1, 0.5)

    return processed_frame, has_ball_in_gripper_range, color_of_ball