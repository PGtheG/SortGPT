import time

import cv2
import numpy as np
from robomaster import camera

BALL_DETECTION_RATE = 0.2 # Range: 0 - 1
BALL_MIN_AREA = 300
BALL_MIN_RADIUS = 5
BALL_MAX_RADIUS = 60
COLOR_BOUNDS = {
    "red": (np.array([102, 0, 0]), np.array([255, 50, 50])),
    "yellow": (np.array([102, 102, 0]), np.array([255, 255, 50])),
    "green": (np.array([0, 102, 0]), np.array([50, 255, 50])),
    "blue": (np.array([0, 50, 204]), np.array([153, 204, 255]))
}

def camera_test(robot):
    robot_camera = robot.camera

    robot_camera.start_video_stream(display=True, resolution=camera.STREAM_720P)
    time.sleep(20)

    robot_camera.stop_video_stream()
    robot.close()


def draw_ball(frame, contour_list, red=255, green=255, blue=255):
    for contour in contour_list:
        area = cv2.contourArea(contour)
        if area > BALL_MIN_AREA:
            center = cv2.moments(contour)
            if center["m00"] != 0:
                cx = int(center["m10"] / center["m00"])
                cy = int(center["m01"] / center["m00"])
                radius = int(cv2.boundingRect(contour)[2] / 2)  # You can adjust how you calculate radius

                cv2.circle(frame, (cx, cy), radius, (red, green, blue), 2)

                text = f"Area: {area:.2f}, radius: {radius}, Pos X: {cx}, Pos Y: {cy}"
                cv2.putText(frame, text, (cx - 50, cy - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)


def filter_circular_contours(contour_list):
    filtered_contours = []
    for contour in contour_list:
        area = cv2.contourArea(contour)
        if area > BALL_MIN_AREA:
            perimeter = cv2.arcLength(contour, True)
            if perimeter > 0:
                circularity = 4 * np.pi * (area / (perimeter * perimeter))
                if circularity > BALL_DETECTION_RATE:
                    (_, radius) = cv2.minEnclosingCircle(contour)
                    if BALL_MIN_RADIUS <= radius <= BALL_MAX_RADIUS:
                        filtered_contours.append(contour)

    return filtered_contours


def choose_best_ball(all_contours):
    best_ball = None
    biggest_ball_area = 0

    for contour in all_contours:
        current_ball_area = cv2.contourArea(contour)

        if current_ball_area > biggest_ball_area:
            biggest_ball_area = current_ball_area
            best_ball = contour

    return best_ball

def observate_camera(robot_camera):
    frame = robot_camera.read_cv2_image(strategy="newest")
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    all_contours = []

    for color, (lower_bound, upper_bound) in COLOR_BOUNDS.items():
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # draw_ball(frame, contours, red=0, green=0, blue=0) # for debugging purposes (black = contours)
        balls = filter_circular_contours(contours)
        # draw_ball(frame, balls, red=255, green=255, blue=255) # for debugging purposes (white = circular objects)
        all_contours.extend(balls)

    best_ball = choose_best_ball(all_contours)

    if best_ball is not None:
        draw_ball(frame, [best_ball], red=0, blue=0)

    cv2.imshow("Ball Detection", frame)

    return best_ball
