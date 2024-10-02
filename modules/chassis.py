import time

from helper.position import calc_turn, calc_distance

def handle_moving(robot, ball):
    degree = calc_turn(ball)
    if degree > 1 or degree < -1:
        turn(robot, degree)

    distance = calc_distance(ball)
    if distance > 0:
        move_forward(robot, distance, speed=0.5)

def move_forward(robot, length, speed=1.0):
    chassis = robot.chassis
    chassis.move(x=length, xy_speed=speed).wait_for_completed()
    time.sleep(1)

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
