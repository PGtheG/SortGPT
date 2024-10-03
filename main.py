import cv2
import threading

from robomaster import robot, camera

from helper.box import get_box_by_color
from modules import camera as mod_camera
from modules import arm as mod_arm
from modules import chassis as mod_chassis
from modules import gripper as mod_gripper

HAS_BALL_IN_GRIPPER = False
COLOR_OF_BALL = None
LATEST_FRAME = None
FRAME_LOCK = threading.Lock()
SPIN_COUNTER = 0


def init_robot():
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")

    mod_arm.move_around(ep_robot)
    mod_gripper.gripper_open(ep_robot)

    return ep_robot

def start_video_stream(robot_camera):
    robot_camera.start_video_stream(display=False, resolution=camera.STREAM_720P)


def handle_gpt(robot, robot_camera):
    frame_to_draw  = handle_search(robot, robot_camera)

    if frame_to_draw is not None:
        cv2.imshow("RoboMaster Camera Feed", frame_to_draw)

def change_position(robot):
    global SPIN_COUNTER

    if SPIN_COUNTER == 36:
        mod_chassis.move_left(robot, 0.5, 0.5)
    elif SPIN_COUNTER == 72:
        mod_chassis.move_right(robot, 0.5, 0.5)
        SPIN_COUNTER = 0


def handle_search(robot, robot_camera):
    global HAS_BALL_IN_GRIPPER
    global COLOR_OF_BALL
    global SPIN_COUNTER
    frame = robot_camera.read_cv2_image(timeout=3, strategy="newest")

    # Mode 1: Search and grip ball
    if HAS_BALL_IN_GRIPPER is False:
        print('Ball mode')
        frame_to_draw, HAS_BALL_IN_GRIPPER, COLOR_OF_BALL = mod_camera.search_ball(robot, frame, robot_camera)

        return frame_to_draw

    # Mode 2: Search box and release ball
    else:
        print('Box mode')
        box_nr = get_box_by_color(COLOR_OF_BALL)
        marker_info, SPIN_COUNTER = mod_camera.handle_search_box(robot, box_nr, SPIN_COUNTER)

        if marker_info:
            SPIN_COUNTER = 0
            frame_to_draw, still_working = mod_camera.handle_marker(robot, robot_camera, marker_info)
            HAS_BALL_IN_GRIPPER = still_working

            return frame_to_draw
        else:
            change_position(robot)

        return frame


# Main function to run the program
if __name__ == '__main__':
    # INITIALIZE
    ep_robot = init_robot()
    robot_camera = ep_robot.camera
    video_thread = threading.Thread(target=start_video_stream, args=(robot_camera,))
    video_thread.daemon = True
    video_thread.start()
    frame_count = 0

    # MAIN LOOP
    while True:
        frame_count += 1
        if frame_count % 3 == 0:
            handle_gpt(ep_robot, robot_camera)

        if frame_count > 100000:
            print(f"Frame count to high ({frame_count}), need to reset")
            frame_count = 0

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # CLEANUP
    robot_camera.stop_video_stream()
    ep_robot.close()
    cv2.destroyAllWindows()
    print('Finished')