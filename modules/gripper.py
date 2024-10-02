def gripper_open(robot):
    gripper = robot.gripper
    gripper.open(power=50)

def gripper_close(robot):
    gripper = robot.gripper
    gripper.close(power=50)
