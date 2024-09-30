import time

def gripper_test(robot):
    gripper = robot.gripper

    gripper.open(power=50)
    time.sleep(1)
    gripper.pause()

    gripper.close(power=50)
    time.sleep(1)
    gripper.pause()

    robot.close()
