from robomaster import robot

from modules.camera import camera_test
from modules.gripper import gripper_test

def init_robot():
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")

    return ep_robot

if __name__ == '__main__':
    # INIT ROBOT
    robot = init_robot()

    # TEST FUNCTIONS
    # camera_test(robot)
    # gripper_test(robot)
