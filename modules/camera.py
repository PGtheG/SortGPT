import time
from robomaster import camera

def camera_test(robot):
    robot_camera = robot.camera

    robot_camera.start_video_stream(display=True, resolution=camera.STREAM_720P)
    time.sleep(20)

    robot_camera.stop_video_stream()

    robot.close()