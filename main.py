from robomaster import robot

from modules.camera import camera_test, detect_and_draw_balls
from modules.gripper import gripper_test
from modules.sound import test_sound


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
    detect_and_draw_balls(robot)
    # test_sound(robot)