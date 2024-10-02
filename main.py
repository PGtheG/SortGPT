import cv2
import threading

from robomaster import robot, camera

from helper.box import get_box_by_color
from modules import camera as mod_camera
from modules import arm as mod_arm
from modules import gripper as mod_gripper

HAS_BALL_IN_GRIPPER = False
COLOR_OF_BALL = None
LATEST_FRAME = None
FRAME_LOCK = threading.Lock()

def init_robot():
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")  # Connect to the robot

    mod_arm.move_around(ep_robot)
    mod_gripper.gripper_open(ep_robot)

    return ep_robot


def start_video_stream(robot_camera):
    robot_camera.start_video_stream(display=False, resolution=camera.STREAM_720P)  # Start without displaying


def get_frame(robot_camera):
    return robot_camera.read_cv2_image(timeout=1, strategy="pipeline")


def handle_gpt(robot, frame):
    frame_to_draw  = handle_search(robot, frame)

    if frame_to_draw is not None:
        cv2.imshow("RoboMaster Camera Feed", frame_to_draw)
    else:
        cv2.imshow("RoboMaster Camera Feed", frame)


def handle_search(robot, frame):
    global HAS_BALL_IN_GRIPPER
    global COLOR_OF_BALL

    # Mode 1: Search and grip ball
    if HAS_BALL_IN_GRIPPER is False:
        print('Search ball mode')
        frame_to_draw, HAS_BALL_IN_GRIPPER, COLOR_OF_BALL = mod_camera.search_ball(robot, frame)

        return frame_to_draw

    # Mode 2: Search box and release ball
    else:
        print('Search box mode')
        box_nr = get_box_by_color(COLOR_OF_BALL)
        marker_info = mod_camera.handle_search_box(robot, box_nr)

        if marker_info:
            frame_to_draw = mod_camera.handle_marker(robot, frame, marker_info)

            return frame_to_draw

        # Switch back to Mode 1 when Ball is released
        # HAS_BALL_IN_GRIPPER = False
        return frame


# Main function to run the program
if __name__ == '__main__':
    # INITIALIZE
    ep_robot = init_robot()
    robot_camera = ep_robot.camera
    video_thread = threading.Thread(target=start_video_stream, args=(robot_camera,))
    video_thread.daemon = True
    video_thread.start()

    # MAIN LOOP
    while True:
        frame = get_frame(robot_camera)
        if frame is not None:
            handle_gpt(ep_robot, frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # CLEANUP
    robot_camera.stop_video_stream()
    ep_robot.close()
    cv2.destroyAllWindows()
    print('Finished')
