import time

import cv2
import numpy as np
from robomaster import camera

BALL_DETECTION_RATE = 0.2 # Range: 0 - 1
BALL_MIN_AREA = 300
BALL_MIN_RADIUS = 5
BALL_MAX_RADIUS = 60
COLOR_BOUNDS = {
    'green': (np.array([0, 128, 0]), np.array([100, 255, 100])),
    'yellow': (np.array([0, 200, 200]), np.array([100, 255, 255])),
    'red': (np.array([0, 0, 128]), np.array([100, 100, 255])),
    'blue': (np.array([200, 0, 0]), np.array([255, 100, 100]))
}
ROI_START_Y = 600
ROI_END_Y = 700
ROI_START_X = 500
ROI_END_X = 800

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

def process_frame(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    all_contours = []

    for color, (lower_bound, upper_bound) in COLOR_BOUNDS.items():
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        balls = filter_circular_contours(contours)
        all_contours.extend(balls)

    best_ball = choose_best_ball(all_contours)

    if best_ball is not None:
        draw_ball(frame, [best_ball], red=0, blue=0)

    return best_ball, frame

def observate_camera(frame):
    best_ball, processed_frame = process_frame(frame)

    return best_ball, processed_frame


def handle_color_in_gripper(frame):
    gripper_roi = frame[ROI_START_Y:ROI_END_Y, ROI_START_X:ROI_END_X]

    for color_name, (lower_bound, upper_bound) in COLOR_BOUNDS.items():
        mask = cv2.inRange(gripper_roi, lower_bound, upper_bound)
        color_pixels = cv2.countNonZero(mask)

        if color_pixels > 2000:
            cv2.rectangle(frame, (ROI_START_X, ROI_START_Y), (ROI_END_X, ROI_END_Y), (0, 255, 0), 2)
            print(f"{color_name} has {color_pixels} pixels")

            return False, frame

    cv2.rectangle(frame, (ROI_START_X, ROI_START_Y), (ROI_END_X, ROI_END_Y), (0, 255, 255), 2)

    return True, frame
