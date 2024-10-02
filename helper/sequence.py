import time

import modules.gripper as mod_gripper
import modules.chassis as mod_chassis
import modules.arm as mod_arm

###########################
# GRAB BALL AND TURN AROUND
###########################
def grab_turn(robot):
    mod_arm.lowtograb(robot)
    time.sleep(1)
    mod_gripper.gripper_close(robot)
    time.sleep(1)
    mod_arm.moveabout(robot)
    time.sleep(1)
    mod_chassis.move_backwards(robot, 0.1, 0.1)
    mod_chassis.turn(robot, 180, 100)
    mod_gripper.gripper_open(robot)

###########################
# GRAB BALL
###########################
def grab_ball(robot):
    mod_arm.lowtograb(robot)
    mod_chassis.move_forward(robot, 0.2, 0.5)
    mod_gripper.gripper_close(robot)
    mod_arm.moveabout(robot)
    mod_chassis.move_backwards(robot, 0.2, 0.5)
    mod_gripper.gripper_open(robot)


# ###########################
# # DROP BALL INTO BOX
# ###########################
def drop_turn(robot):
    mod_arm.lowtograb(robot)
    time.sleep(1)
    mod_gripper.gripper_close(robot)
    time.sleep(1)
    mod_arm.moveabout(robot)
    time.sleep(1)
    mod_arm.high(robot)
    time.sleep(1)
    mod_chassis.move_forward(robot, 0.25, 0.5)
    time.sleep(1)
    mod_gripper.gripper_open(robot)
    time.sleep(1)
    mod_chassis.move_backwards(robot, 0.25, 0.5)
    time.sleep(1)
    mod_chassis.turn(robot, 180, 100)
    time.sleep(1)
    mod_arm.moveabout(robot)
    time.sleep(1)

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
