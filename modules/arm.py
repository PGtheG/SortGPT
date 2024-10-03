from robomaster import robotic_arm

def move_around(robot):
    arm = robot.robotic_arm
    arm.moveto(x=180, y=0).wait_for_completed()

def high(robot):
    arm = robot.robotic_arm
    arm.moveto(x=0, y=180).wait_for_completed()

def low_to_grab(robot):
    arm = robot.robotic_arm
    arm.moveto(x=180, y=-50).wait_for_completed()
