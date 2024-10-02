import cv2
from robomaster import robot, camera

import modules.camera as mod_camera
import modules.gripper as mod_gripper
import modules.sound as mod_sound
import modules.chassis as mod_chassis


def init_robot():
    init_robot = robot.Robot()
    init_robot.initialize(conn_type="ap")

    return init_robot

def init_cam(init_cam_robot):
    robot_camera = init_cam_robot.camera
    robot_camera.start_video_stream(display=False, resolution=camera.STREAM_720P)

    return robot_camera

if __name__ == '__main__':
    # INIT ROBOT
    ep_robot = init_robot()
    ep_camera = init_cam(ep_robot)

    # TEST FUNCTIONS
    # mod_camera.camera_test(robot)
    # mod_gripper.gripper_test(robot)
    # mod_sound.test_sound(robot)


    # MAIN FUNCTION
    # while True:
    #     ball = observate_camera(ep_camera)
    #
    #     if ball is not None:
    #         mod_chassis.handle_moving(ep_robot, ball)
    #
    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         break
    #
    # ep_camera.stop_video_stream()
    # cv2.destroyAllWindows()
    # print('done')

