import time

import modules.gripper as mod_gripper
import modules.chassis as mod_chassis
import modules.arm as mod_arm

def release_ball(robot):
    mod_arm.high(robot)
    mod_chassis.move_forward(robot, 0.3, 1.0)
    mod_gripper.gripper_open(robot)
    mod_chassis.move_backwards(robot, 0.5, 1.0)
    mod_chassis.turn(robot, 180, 360)
    mod_arm.move_around(robot)

###########################
# GRAB BALL
###########################
def grab_ball(robot):
    mod_arm.low_to_grab(robot)
    mod_chassis.move_forward(robot, 0.2, 0.5)
    mod_gripper.gripper_close(robot)
    mod_arm.move_around(robot)
    mod_chassis.move_backwards(robot, 0.3, 1.0)

###########################
# SEARCH WHILE ROTATING
###########################
def search_ball(robot):
    mod_chassis.turn(robot, 360, 100)

###########################
# SEARCH WHILE ROTATING AND MOVING
###########################
def search_move(robot):
    mod_chassis.turn(robot, 90, 100)
    mod_chassis.move_left(robot, 0.5, 0.5)
    mod_chassis.turn(robot, -450, 100)
    mod_chassis.move_left(robot, 0.5, 0.5)
    mod_chassis.turn(robot, -450, 100)
    mod_chassis.move_right(robot, 1, 0.5)
    mod_chassis.turn(robot, -450, 100)
    mod_chassis.move_right(robot, 1.5, 0.5)
    mod_chassis.turn(robot, -450, 100)
    mod_chassis.move_right(robot, 2, 0.5)
    mod_chassis.turn(robot, -450, 100)
    mod_chassis.move_right(robot, 2.5, 0.5)
    mod_chassis.turn(robot, -450, 100)
    mod_chassis.move_right(robot, 3, 0.5)
    mod_chassis.turn(robot, -450, 100)
