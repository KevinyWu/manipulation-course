import os, json, threading, argparse
from robot.robot import Robot

# Square and pose types
SQUARES = ['A', 'B', 'C', 'D', 'E', 'F'] + list(range(0, 9))
POSE_TYPES = ['hover_over', 'pre_grasp', 'grasp', 'post_grasp']

def parse_arguments():
    parser = argparse.ArgumentParser(description='Record positions for tic-tac-toe game.')
    parser.add_argument('-l', '--leader', action='store_true', default=False, 
                        help='Enable teleoperation using a leader arm.')
    return parser.parse_args()

def load_robot_settings(args):
    with open('../config.json') as f:
        config = json.load(f)
    arm_config = config['arm']
    leader_config = config['leader'] if args.leader else None
    return arm_config, leader_config

def initialize_robots(arm_config, leader_config):
    arm = Robot(device_name=arm_config['device_name'], 
                servo_ids=arm_config['servo_ids'],
                velocity_limit=arm_config['velocity_limit'])
    leader = None
    if leader_config:
        leader = Robot(device_name=leader_config['device_name'], 
                    servo_ids=leader_config['servo_ids'])
        leader.set_trigger_torque()
    return arm, leader

# TODO: Manual position recording is not that accurate
# Function to record positions manually
def record_position(arm, square, pose_type):
    arm._disable_torque()
    print(f'Move the arm to the {pose_type} position of square {square}. Press enter to record. Press s to skip.')
    user_input = input()
    if user_input == 's':
        return None
    arm._enable_torque()
    input()
    pos = arm.read_position()
    pos = [int(p) for p in pos]
    if pose_type in ['grasp', 'post_grasp']:
        pos[-1] -= 50
    return pos

# Function to record positions with leader arm
def record_position_with_leader(arm, leader, square, pose_type):
    print(f'Move the arm to the {pose_type} position of square {square}.')
    # Wait for user input to stop teleoperation
    stop = threading.Event()
    def wait_for_input(stop):
        input('Press enter to record.')
        stop.set()
    thread = threading.Thread(target=wait_for_input, args=(stop,))
    thread.start()
    # Teleoperation
    while not stop.is_set():
        pos = leader.read_position()
        arm.set_goal_pos(pos)
    thread.join()
    # Record position
    pos = [int(p) for p in pos]
    return pos

def main():
    args = parse_arguments()
    arm_config, leader_config = load_robot_settings(args)
    arm, leader = initialize_robots(arm_config, leader_config)
    
    # Go to game start position
    arm.set_and_wait_goal_pos(arm_config['game_pos'])

    # Create positions.json if it does not exist
    if not os.path.exists('positions.json'):
        with open('positions.json', 'w') as f:
            json.dump({}, f)
    with open('positions.json') as f:
        positions = json.load(f)

    # Record positions for each square and pose type
    for square in SQUARES:
        print(f'Record positions for square {square}. Press enter to record. Press s to skip.')
        user_input = input()
        if user_input == 's':
            continue
        if square not in positions:
            positions[square] = {}
        for pose_type in POSE_TYPES:
            if not args.leader:
                pos = record_position(arm, square, pose_type)
            else:
                pos = record_position_with_leader(arm, leader, square, pose_type)
            if pos is not None:
                positions[square][pose_type] = pos
    with open('positions.json', 'w') as f:
        json.dump(positions, f, indent=4)

    # Go to home position and disable torque
    arm.set_and_wait_goal_pos(arm_config['home_pos'])
    arm._disable_torque()

if __name__ == "__main__":
    main()
