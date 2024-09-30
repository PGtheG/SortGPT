import time
from robomaster import robot
from robomaster import camera

if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")
    ep_camera = ep_robot.camera

    ep_camera.start_video_stream(display=True, resolution=camera.STREAM_720P)
    time.sleep(20)

    ep_camera.stop_video_stream()
    ep_robot.close()