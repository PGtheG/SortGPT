import time


def gripper_open(robot):
    gripper = robot.gripper
    gripper.open(power=50)
    time.sleep(1)

def gripper_close(robot):
    gripper = robot.gripper
    gripper.close(power=50)
    time.sleep(1)
