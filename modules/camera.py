import time

import cv2
import numpy as np
from robomaster import robot

from modules import chassis as mod_chassis
from modules import arm as mod_arm
from helper import sequence as help_sequence

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
ROI_START_Y = 450
ROI_END_Y = 550
ROI_START_X = 550
ROI_END_X = 750
THRESHOLD = 1500
DETECTED_MARKER_INFO = None
BOX_NR = 0

def draw_circles(frame, contour_list, red=255, green=255, blue=255):
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
        draw_circles(frame, contours, red=0, green=0, blue=0) # for debugging purposes (black = contours)
        balls = filter_circular_contours(contours)
        draw_circles(frame, balls, red=255, green=255, blue=255) # for debugging purposes (white = circular objects)
        all_contours.extend(balls)

    best_ball = choose_best_ball(all_contours)

    if best_ball is not None:
        draw_circles(frame, [best_ball], red=0, blue=0)

    return best_ball, frame

def search_for_ball(frame):
    best_ball, processed_frame = process_frame(frame)

    return best_ball, processed_frame

def search_ball(robot, frame):
    ball, processed_frame = search_for_ball(frame)

    if ball is None:
        # Advanced logic which searches for ball needed
        print('no ball found, start searching...')
        mod_chassis.turn(robot, 20, 30)

        return processed_frame, False, None

    else:
        frame_with_ball, has_ball_in_gripper_range, color_of_ball = mod_chassis.handle_moving(robot, ball, processed_frame)
        if has_ball_in_gripper_range:
            help_sequence.grab_ball(robot)

        return frame_with_ball, has_ball_in_gripper_range, color_of_ball


def handle_color_in_gripper(frame):
    gripper_roi = frame[ROI_START_Y:ROI_END_Y, ROI_START_X:ROI_END_X]

    for color_name, (lower_bound, upper_bound) in COLOR_BOUNDS.items():
        mask = cv2.inRange(gripper_roi, lower_bound, upper_bound)
        color_pixels = cv2.countNonZero(mask)

        if color_pixels > THRESHOLD:
            cv2.rectangle(frame, (ROI_START_X, ROI_START_Y), (ROI_END_X, ROI_END_Y), (0, 255, 0), 2)
            print(f"{color_name} has {color_pixels} pixels")

            return True, frame, color_name

    cv2.rectangle(frame, (ROI_START_X, ROI_START_Y), (ROI_END_X, ROI_END_Y), (0, 255, 255), 2)

    return False, frame, None


def handle_search_box(robot, box_nr):
    global DETECTED_MARKER_INFO
    global BOX_NR

    BOX_NR = box_nr
    search_box_with_vision(robot)

    if DETECTED_MARKER_INFO:
        marker_info = DETECTED_MARKER_INFO
        DETECTED_MARKER_INFO = None

        return marker_info

    else:
        mod_chassis.turn(robot, 45, 100)

    return None


def search_box_with_vision(robot):
    robot_vision = robot.vision
    robot_vision.sub_detect_info(name='marker', callback=marker_detected)


def marker_detected(marker_info):
    global DETECTED_MARKER_INFO
    for info in marker_info:
        x, y, w, h, number = info

        if int(number) == BOX_NR:
            DETECTED_MARKER_INFO = (x, y, w, h, number)
            break  # Exit once we find the matching marker


def draw_marker(frame, marker_info):
    frame_height, frame_width = frame.shape[:2]
    x, y, w, h, number = marker_info

    rect_x = int(x * frame_width)
    rect_y = int(y * frame_height)
    rect_width = int(w * frame_width)
    rect_height = int(h * frame_height)

    top_left_x = int(rect_x - (rect_width / 2))
    top_left_y = int(rect_y - (rect_height / 2))
    bottom_right_x = int(rect_x + (rect_width / 2))
    bottom_right_y = int(rect_y + (rect_height / 2))

    cv2.rectangle(frame, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), (0, 0, 0), 2)

    return frame, rect_x, rect_y

def adjust_position(robot, rect_x, rect_y):
    lower_middle = 600
    upper_middle = 720
    lower_distance = 350
    upper_distance = 400
    has_position = True

    if rect_x < lower_middle:
        mod_chassis.move_left(robot, 0.1, 0.5)
        has_position = False

    elif rect_x > upper_middle:
        mod_chassis.move_right(robot, 0.1, 0.5)
        has_position = False

    elif rect_y < lower_distance:
        mod_chassis.move_forward(robot, 0.1, 0.5)
        has_position = False

    elif rect_y > upper_distance:
        mod_chassis.move_backwards(robot, 0.1, 0.5)
        has_position = False

    return has_position


def handle_marker(robot, frame, marker_info):
    frame_to_draw, rect_x, rect_y = draw_marker(frame, marker_info)
    has_position = adjust_position(robot, rect_x, rect_y)

    if has_position:
        help_sequence.release_ball(robot)

    return frame_to_draw
