import threading
from time import sleep

import cv2
import numpy as np

from helper.position import calc_turn_for_marker
from helper.sequence import pick_ball, grab_ball
from modules import chassis as mod_chassis
from modules import gripper as mod_gripper
from helper import sequence as help_sequence

BALL_DETECTION_RATE = 0.2 # Range: 0 - 1
BALL_MIN_AREA = 500
BALL_MIN_RADIUS = 15
BALL_MAX_RADIUS = 80
COLOR_BOUNDS = {
    'green': (np.array([35, 70, 120]), np.array([95, 255, 255])),
    'yellow': (np.array([20, 100, 100]), np.array([30, 255, 255])),
    'red': (np.array([0, 100, 58]), np.array([10, 255, 255])),
    'blue': (np.array([100, 100, 100]), np.array([140, 255, 255]))
}
ROI_START_Y = 450
ROI_END_Y = 550
ROI_START_X = 550
ROI_END_X = 750

ROI_GRIPPER_BALL_START_Y = 600
ROI_GRIPPER_BALL_END_Y = 700
ROI_GRIPPER_BALL_START_X = 550
ROI_GRIPPER_BALL_END_X = 750

THRESHOLD = 1500
DETECTED_MARKER_INFO = None
DETECTED_MARKER_LOCK = threading.Lock()
BOX_NR = 0
SEARCH_ANGLE = 0
SEARCH_PHASE = 0,
GRAB_TRY_COUNT = 0

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


def choose_best_ball(all_balls):
    best_ball = None
    biggest_ball_area = 0

    for ball in all_balls:
        current_ball_area = cv2.contourArea(ball)

        if current_ball_area > biggest_ball_area:
            biggest_ball_area = current_ball_area
            best_ball = ball

    return best_ball

def process_frame(robot_camera):
    frame = get_newest_frame(robot_camera, True)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    all_balls = []

    for color, (lower_bound, upper_bound) in COLOR_BOUNDS.items():
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        draw_circles(frame, contours, red=0, green=0, blue=0) # for debugging purposes (black = contours)
        balls = filter_circular_contours(contours)
        draw_circles(frame, balls, red=255, green=255, blue=255) # for debugging purposes (white = circular objects)
        all_balls.extend(balls)

    best_ball = choose_best_ball(all_balls)

    if best_ball is not None:
        draw_circles(frame, [best_ball], red=0, blue=0)

    return best_ball, frame

def search_for_ball(robot_camera):
    best_ball, processed_frame = process_frame(robot_camera)

    return best_ball, processed_frame

def get_newest_frame(robot_camera, newest_needed=False):
    # This ugly piece of code is needed, because dji can't implement
    # a function which gives you the newest frame back -.-
    frame = robot_camera.read_cv2_image(timeout=3, strategy="newest")
    if newest_needed:
        sleep(1)
    frame = robot_camera.read_cv2_image(timeout=3, strategy="newest")
    frame = robot_camera.read_cv2_image(timeout=3, strategy="newest")

    return frame


def check_if_ball_is_grabbed(robot_camera):
    frame = get_newest_frame(robot_camera, True)

    ball_roi = frame[ROI_GRIPPER_BALL_START_Y:ROI_GRIPPER_BALL_END_Y, ROI_GRIPPER_BALL_START_X:ROI_GRIPPER_BALL_END_X]

    is_ball_in_gripper, color_name = check_color_in_roi(frame, ball_roi, ROI_GRIPPER_BALL_START_Y, ROI_GRIPPER_BALL_END_Y, ROI_GRIPPER_BALL_START_X, ROI_GRIPPER_BALL_END_X)

    return is_ball_in_gripper, color_name

def is_frame_mostly_white(robot_camera, threshold):
    frame = get_newest_frame(robot_camera, True)
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_white = np.array([0, 0, 150], dtype=np.uint8)  # Lower brightness to allow even darker whites
    upper_white = np.array([180, 80, 255], dtype=np.uint8)

    white_mask = cv2.inRange(hsv_frame, lower_white, upper_white)
    white_pixel_ratio = np.sum(white_mask > 0) / white_mask.size

    print(f"Pixel ratio: {white_pixel_ratio}, threshold: {threshold}")

    return white_pixel_ratio > threshold, frame


def search_ball_in_room(robot, robot_camera):
    global SEARCH_ANGLE, SEARCH_PHASE

    print('Searching for the ball...')

    # Phase 0: Rotating
    if SEARCH_PHASE == 0:
        print("Search phase")
        # Rotate the robot in increments (e.g., 30 degrees at a time)
        mod_chassis.turn(robot, 30, 40)
        SEARCH_ANGLE += 30

        # Check if a full rotation (360 degrees) has been completed
        if SEARCH_ANGLE >= 390:
            SEARCH_ANGLE = 0  # Reset rotation progress
            SEARCH_PHASE = 1  # Switch to movement phase

    # Phase 1: Moving
    else:
        print("Moving phase")
        while True:
            is_white, processed_frame = is_frame_mostly_white(robot_camera, 0.35)

            if is_white:
                print("Detected white wall, turning to find a clearer view")
                mod_chassis.turn(robot, 30, 40)
            else:
                print("Clear view found, proceeding with ball search")
                break
        mod_chassis.move_forward(robot, 0.5, 1.0)
        SEARCH_PHASE = 0

    return


def search_ball(robot, robot_camera):
    global GRAB_TRY_COUNT
    # 1. Check first if ball is already in perfect position
    frame = robot_camera.read_cv2_image(timeout=1, strategy="newest")
    gripper_roi = frame[ROI_GRIPPER_BALL_START_Y:ROI_GRIPPER_BALL_END_Y, ROI_GRIPPER_BALL_START_X:ROI_GRIPPER_BALL_END_X]
    has_color, color_name = check_color_in_roi(frame, gripper_roi, ROI_GRIPPER_BALL_START_Y, ROI_GRIPPER_BALL_END_Y, ROI_GRIPPER_BALL_START_X, ROI_GRIPPER_BALL_END_X)

    if has_color is True:
        pick_ball(robot)
        has_color, color_name = check_color_in_roi(frame, gripper_roi, ROI_GRIPPER_BALL_START_Y, ROI_GRIPPER_BALL_END_Y, ROI_GRIPPER_BALL_START_X, ROI_GRIPPER_BALL_END_X)

        return frame, has_color, color_name

    # 2. If not, search for ball in frame
    ball, processed_frame = search_for_ball(robot_camera)

    if ball is None:
        # Advanced logic which searches for ball needed
        search_ball_in_room(robot, robot_camera)

        return processed_frame, False, None

    else:
        print('Ball found, start driving towards')
        frame_with_ball, has_ball_in_gripper_range, color_of_ball = mod_chassis.handle_moving(robot, ball, robot_camera)
        is_ball_in_gripper = False

        if has_ball_in_gripper_range:
            help_sequence.grab_ball(robot)
            is_ball_in_gripper, color_of_ball = check_if_ball_is_grabbed(robot_camera)

            if is_ball_in_gripper is False:
                mod_gripper.gripper_open(robot)
                GRAB_TRY_COUNT += 1
            else:
                GRAB_TRY_COUNT = 0

            if GRAB_TRY_COUNT >= 3:
                mod_chassis.turn(robot, 90, 50)
                GRAB_TRY_COUNT = 0

        return frame_with_ball, is_ball_in_gripper, color_of_ball


def check_color_in_roi(frame, roi, start_y, end_y, start_x, end_x):
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    for color_name, (lower_bound, upper_bound) in COLOR_BOUNDS.items():
        mask = cv2.inRange(hsv_roi, lower_bound, upper_bound)
        color_pixels = cv2.countNonZero(mask)

        if color_pixels > THRESHOLD:
            cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)
            print(f"{color_name} has {color_pixels} pixels")

            return True, color_name

        else:
            cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), (0, 0, 0), 2)
            print(f"{color_name} has {color_pixels} pixels")

    return False, None



def handle_color_in_gripper(robot_camera):
    frame = robot_camera.read_cv2_image(timeout=1, strategy="newest")
    gripper_roi = frame[ROI_START_Y:ROI_END_Y, ROI_START_X:ROI_END_X]
    has_color, color_name = check_color_in_roi(frame, gripper_roi, ROI_START_Y, ROI_END_Y, ROI_START_X, ROI_END_X)

    cv2.rectangle(frame, (ROI_START_X, ROI_START_Y), (ROI_END_X, ROI_END_Y), (0, 255, 255), 2)

    return has_color, frame, None


def handle_search_box(robot, box_nr, count):
    global DETECTED_MARKER_INFO
    global BOX_NR

    BOX_NR = box_nr
    search_box_with_vision(robot)

    with DETECTED_MARKER_LOCK:
        if DETECTED_MARKER_INFO:
            print('Marker detected')
            marker_info = DETECTED_MARKER_INFO
            DETECTED_MARKER_INFO = None
            return marker_info, count
        else:
            print('No Marker detected, will turn slow')
            mod_chassis.turn(robot, 20, 25)
            count += 1

    return None, count


def search_box_with_vision(robot):
    robot_vision = robot.vision
    robot_vision.sub_detect_info(name='marker', callback=marker_detected)


def marker_detected(marker_info):
    global DETECTED_MARKER_INFO
    with DETECTED_MARKER_LOCK:
        for info in marker_info:
            x, y, w, h, number = info
            if int(number) == BOX_NR:
                DETECTED_MARKER_INFO = (x, y, w, h, number)
                break  # Exit once we find the matching marker


def draw_marker(robot_camera, marker_info):
    frame = get_newest_frame(robot_camera, True)
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

    return frame, rect_x, rect_y, rect_width, rect_height

def adjust_position(robot, frame, rect_x, rect_y):
    lower_middle = 530
    upper_middle = 800
    lower_distance = 330
    upper_distance = 380
    adjust_degree = 5
    has_position = True
    print("Adjust position:")

    degree = calc_turn_for_marker(rect_x)

    if degree > adjust_degree or degree < (adjust_degree * -1):
        mod_chassis.turn(robot, degree, 50)
        has_position = False
        print(f"Turn, degree: {degree}")

    if rect_y < lower_distance:
        current_distance = lower_distance - rect_y
        print(f"move forward, distance: {current_distance}")

        if current_distance > 160:
            mod_chassis.move_forward(robot, 1.2, 1.0)
        elif current_distance > 150:
            mod_chassis.move_forward(robot, 0.8, 1.0)
        elif current_distance > 120:
            mod_chassis.move_forward(robot, 0.4, 1.0)
        elif current_distance > 110:
            mod_chassis.move_forward(robot, 0.3, 1.0)
        else:
            mod_chassis.move_forward(robot, 0.2, 0.5)

        has_position = False

    elif rect_y > upper_distance:
        mod_chassis.move_backwards(robot, 0.15, 0.5)
        has_position = False
        print("move backwards")

    print(f"Has position: {has_position}")

    cv2.rectangle(frame, (lower_middle, lower_distance), (upper_middle, upper_distance), (0, 0, 0), 2)

    return frame, has_position


def handle_marker(robot, robot_camera, marker_info):
    processed_frame, rect_x, rect_y, rect_width, rect_height = draw_marker(robot_camera, marker_info)
    frame_to_draw, has_position = adjust_position(robot, processed_frame, rect_x, rect_y)
    still_working = True

    if has_position:
        print("Release ball")
        help_sequence.release_ball(robot)
        still_working = False

    return frame_to_draw, still_working
