import json, time
from robot.robot import Robot

# Load robot settings
with open('../config.json') as f:
    config = json.load(f)
    arm_config = config['arm']

# Load game positions
with open('positions.json') as f:
    positions = json.load(f)

# Dynamixel configuration
arm = Robot(device_name=arm_config['device_name'], 
            servo_ids=arm_config['servo_ids'],
            velocity_limit=arm_config['velocity_limit'])

# Go to game start position
arm.set_and_wait_goal_pos(arm_config['game_pos'])

def move_piece(start, end):
    arm.set_and_wait_goal_pos(positions[start]['hover_over'])
    arm.set_and_wait_goal_pos(positions[start]['pre_grasp'])
    arm.set_and_wait_goal_pos(positions[start]['grasp'])
    arm.set_and_wait_goal_pos(positions[start]['post_grasp'])
    arm.set_and_wait_goal_pos(positions[end]['post_grasp'])
    arm.set_and_wait_goal_pos(positions[end]['grasp'])
    arm.set_and_wait_goal_pos(positions[end]['pre_grasp'])
    arm.set_and_wait_goal_pos(positions[end]['hover_over'])
    arm.set_and_wait_goal_pos(arm_config['game_pos'])


# Sample game
move_piece('A', '4')
time.sleep(3)
move_piece('B', '5')
time.sleep(3)
move_piece('C', '6')
time.sleep(3)
move_piece('D', '1')
time.sleep(3)
move_piece('E', '8')

# Go to home position and disable torque
arm.set_and_wait_goal_pos(arm_config['rest_pos'])
arm._disable_torque()
