from helper.position import calc_turn
from modules import camera as mod_camera


def handle_moving(robot, ball, robot_camera):
    degree = calc_turn(ball)
    if degree > 3 or degree < -3:
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
    attempt = 0
    max_attempts = 3
    has_ball_in_gripper_range = False
    processed_frame = None
    color_of_ball = None

    while attempt < max_attempts and not has_ball_in_gripper_range:
        has_ball_in_gripper_range, processed_frame, color_of_ball = mod_camera.handle_color_in_gripper(robot_camera)

        if has_ball_in_gripper_range:
            print("Ball is in gripper range.")
            break

        move_forward(robot, 0.2, 0.5)
        attempt += 1
        print(f"Attempt {attempt}/{max_attempts}")

    return processed_frame, has_ball_in_gripper_range, color_of_ball