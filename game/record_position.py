import argparse, json, threading
import numpy as np
from robot.robot import Robot

# Load configuration
with open('config.json') as f:
    config = json.load(f)

# Argument parsing
parser = argparse.ArgumentParser(description='Teleoperate real robot.')
parser.add_argument('-l', '--left', action='store_true', 
                    help='Enable teleoperation of left arm.')
parser.add_argument('-r', '--right', action='store_true', 
                    help='Enable teleoperation of right arm.')
args = parser.parse_args()

L = args.left
R = args.right
if not L and not R: # Bimanual is default
    L = True
    R = True

# Dynamixel configuration
if L:
    Lfollower = Robot(device_name=config['Lfollower']['device_name'], 
                      servo_ids=config['Lfollower']['servo_ids'],
                      velocity_limit=config['Rfollower']['velocity_limit'])
    Lleader = Robot(device_name=config['Lleader']['device_name'], 
                    servo_ids=config['Lleader']['servo_ids'])
    Lleader.set_trigger_torque()
if R:
    Rfollower = Robot(device_name=config['Rfollower']['device_name'], 
                      servo_ids=config['Rfollower']['servo_ids'],
                      velocity_limit=config['Rfollower']['velocity_limit'])
    Rleader = Robot(device_name=config['Rleader']['device_name'], 
                    servo_ids=config['Rleader']['servo_ids'])
    Rleader.set_trigger_torque()

# Seperate thread to stop teleoperation
stop = threading.Event()
def wait_for_input(stop):
    input('\nPress Enter to stop teleoperation...\n\n')
    stop.set()
thread = threading.Thread(target=wait_for_input, args=(stop,))
thread.start()

# Teleoperation
Llimits_max = config['Lfollower']['max_position_limit']
Llimits_min = config['Lfollower']['min_position_limit']
Rlimits_max = config['Rfollower']['max_position_limit']
Rlimits_min = config['Rfollower']['min_position_limit']
try:
    if L and R:
        while not stop.is_set():
            l_pos = Lleader.read_position()
            r_pos = Rleader.read_position()
            l_pos = np.clip(Lleader.read_position(),
                            Llimits_min, Llimits_max)
            r_pos = np.clip(Rleader.read_position(),
                            Rlimits_min, Rlimits_max)
            Lfollower.set_goal_pos(l_pos)
            Rfollower.set_goal_pos(r_pos)
    elif L:
        while not stop.is_set():
            pos = Lleader.read_position()
            pos = np.clip(Lleader.read_position(),
                          Llimits_min, Llimits_max)
            Lfollower.set_goal_pos(pos)
    elif R:
        while not stop.is_set():
            pos = Rleader.read_position()
            pos = np.clip(Rleader.read_position(),
                          Rlimits_min, Rlimits_max)
            Rfollower.set_goal_pos(pos)
except Exception as e:
    print(f'An error occurred: {e}')
finally:
    print('Teleoperation stopped, disabling torque.\n')
    if L:
        Lleader._disable_torque()
        Lfollower._disable_torque()
    if R:
        Rleader._disable_torque()
        Rfollower._disable_torque()
