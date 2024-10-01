import time

import cv2
import numpy as np
from robomaster import camera

def camera_test(robot):
    robot_camera = robot.camera

    robot_camera.start_video_stream(display=True, resolution=camera.STREAM_720P)
    time.sleep(20)

    robot_camera.stop_video_stream()
    robot.close()

def draw_ball(frame, contour_list):
    for contour in contour_list:
        area = cv2.contourArea(contour)
        if area > 100:
            center = cv2.moments(contour)
            if center["m00"] != 0:
                cx = int(center["m10"] / center["m00"])
                cy = int(center["m01"] / center["m00"])
                radius = int(cv2.boundingRect(contour)[2] / 2)  # You can adjust how you calculate radius

                cv2.circle(frame, (cx, cy), radius, (255, 255, 255), 2)



def detect_and_draw_ball(robot):
    red_lower = np.array([102, 0, 0])
    red_upper = np.array([255, 50, 50])
    yellow_lower = np.array([102, 102, 0])
    yellow_upper = np.array([255, 255, 50])
    green_lower = np.array([0, 102, 0])
    green_upper = np.array([50, 255, 50])
    blue_lower = np.array([0, 100, 204])
    blue_upper = np.array([153, 204, 255])

    robot_camera = robot.camera
    robot_camera.start_video_stream(display=False, resolution=camera.STREAM_720P)

    while True:
        frame = robot_camera.read_cv2_image(strategy="newest")
        if frame is None:
            continue

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        red = cv2.inRange(hsv, red_lower, red_upper)
        yellow = cv2.inRange(hsv, yellow_lower, yellow_upper)
        green = cv2.inRange(hsv, green_lower, green_upper)
        blue = cv2.inRange(hsv, blue_lower, blue_upper)

        contours_red, _= cv2.findContours(red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_yellow, _= cv2.findContours(yellow, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_green, _= cv2.findContours(green, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_blue, _= cv2.findContours(blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        draw_ball(frame, contours_red)
        draw_ball(frame, contours_yellow)
        draw_ball(frame, contours_green)
        draw_ball(frame, contours_blue)

        cv2.imshow("Ball Detection", frame)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.stop_video_stream()
    robot.close()
    cv2.destroyAllWindows()