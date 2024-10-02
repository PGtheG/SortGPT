import cv2
import threading
from robomaster import robot

from modules.camera import observate_camera, process_frame
from modules.chassis import handle_moving


# Initialize the RoboMaster EP Core
def init_robot():
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="ap")  # Connect to the robot
    return ep_robot

# Function to start the video stream
def start_video_stream(robot_camera):
    robot_camera.start_video_stream(display=False)  # Start without displaying

# Main function to run the program
if __name__ == '__main__':
    # Initialize the robot
    ep_robot = init_robot()
    robot_camera = ep_robot.camera

    # Start the video stream in a separate thread
    video_thread = threading.Thread(target=start_video_stream, args=(robot_camera,))
    video_thread.daemon = True  # Ensure thread exits when main program exits
    video_thread.start()

    # Main loop to capture and display the camera feed
    while True:
        frame = robot_camera.read_cv2_image(timeout=3, strategy="pipeline")
        if frame is not None:
            ball, processed_frame = observate_camera(frame)

            if ball is not None:
                new_frame = handle_moving(ep_robot, ball, processed_frame)

                cv2.imshow("RoboMaster Camera Feed", new_frame)

            else:
                cv2.imshow("RoboMaster Camera Feed", processed_frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup
    robot_camera.stop_video_stream()
    ep_robot.close()  # Close the robot connection
    cv2.destroyAllWindows()  # Close OpenCV windows
    print('Finished')
