import math

import cv2
import numpy as np
from numpy.f2py.auxfuncs import throw_error
from scipy.optimize import curve_fit

OFFSET = 0 # in m

def calc_turn(ball, image_width=1280, fov=90):
    robot_x = image_width // 2

    center = cv2.moments(ball)
    if center["m00"] == 0:
        throw_error(center)

    ball_x = int(center["m10"] / center["m00"])
    pixel_offset_x = ball_x - robot_x
    pixels_per_degree = image_width / fov

    return pixel_offset_x / pixels_per_degree

def calc_distance(ball):
    value = 360
    distance = get_distance_for_y(value)
    print(f"The distance for y = {value} is {distance:.2f} cm.")
    return distance

# Exponential function model
def exponential_func(y, a, b):
    """Exponential function model."""
    return a * np.exp(b * y)

# Given measured data points
y_values = np.array([720, 360, 266, 227, 210])  # y values (in px)
distances = np.array([0, 50, 100, 150, 200])     # Distances (in cm)

# Fit the exponential model to the data
params, _ = curve_fit(exponential_func, y_values, distances)

# Extract the fitted parameters
a, b = params
print(f"Fitted parameters: a = {a:.4f}, b = {b:.4f}")

# Function to calculate distance using the fitted exponential model
def calculate_exponential_distance(y):
    """Calculate distance in cm for a given y value using the fitted exponential model."""
    return exponential_func(y, a, b)

# Function to get distance based on y value
def get_distance_for_y(y):
    """Return the distance for a given y value using the exponential model."""
    if y < 210 or y > 720:  # Adjusting the limits based on the given data
        raise ValueError("y value must be between 210 and 720 inclusive.")
    distance = calculate_exponential_distance(y)
    return distance

