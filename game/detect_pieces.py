import cv2
import numpy as np
import json
from robot.robot import Robot

# sudo apt-get update
# sudo apt-get install libgtk2.0-dev pkg-config
# sudo apt-get install libcanberra-gtk-module libcanberra-gtk3-module
# pip install opencv-python

def preprocess_image(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    return edges

def detect_grid_lines(edges):
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=75, minLineLength=300, maxLineGap=300)
    return lines

def draw_lines(frame, lines):
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

def detect_pieces(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # Define color ranges for red and blue
    lower_red = np.array([0, 120, 70])
    upper_red = np.array([10, 255, 255])
    lower_blue = np.array([94, 80, 2])
    upper_blue = np.array([126, 255, 255])
    mask_red = cv2.inRange(hsv, lower_red, upper_red)
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    return mask_red, mask_blue

def find_piece_positions(mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    positions = []
    for contour in contours:
        if cv2.contourArea(contour) > 500:  # Adjust as needed
            x, y, w, h = cv2.boundingRect(contour)
            positions.append((x, y, w, h))
    return positions

def draw_bounding_boxes(image, positions, color):
    for (x, y, w, h) in positions:
        cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)

def main():
    # Load robot settings
    with open('../config.json') as f:
        config = json.load(f)
        arm_config = config['arm']

    # Dynamixel configuration
    arm = Robot(device_name=arm_config['device_name'], 
                servo_ids=arm_config['servo_ids'],
                velocity_limit=arm_config['velocity_limit'],
                max_position_limit=arm_config['max_position_limit'],
                min_position_limit=arm_config['min_position_limit'],
                position_p_gain=arm_config['position_p_gain'],
                position_i_gain=arm_config['position_i_gain'])

    # Go to home start position
    arm.set_and_wait_goal_pos(arm_config['home_pos'])

    cap = cv2.VideoCapture(0)  # 0 is the default camera

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        edges = preprocess_image(frame)
        lines = detect_grid_lines(edges)
        draw_lines(frame, lines)

        mask_red, mask_blue = detect_pieces(frame)
        red_positions = find_piece_positions(mask_red)
        blue_positions = find_piece_positions(mask_blue)

        draw_bounding_boxes(frame, red_positions, (0, 0, 255))  # Red
        draw_bounding_boxes(frame, blue_positions, (255, 0, 0))  # Blue

        cv2.imshow('Tic Tac Toe Grid Detection', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 13:
            break

    cap.release()
    cv2.destroyAllWindows()
    arm.set_and_wait_goal_pos(arm_config['rest_pos'])
    arm._disable_torque()

if __name__ == '__main__':
    main()
