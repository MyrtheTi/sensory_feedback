"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-01-23 08:59:49
 * @desc Script with utility functions and predefined parameters.
"""

import board
import digitalio
import pandas as pd

VIB_PIN_LIST = [
    {"LEVEL": 0, "PIN": board.D7, "PREV_TIME": -1},
    {"LEVEL": 1, "PIN": board.D8, "PREV_TIME": -1},
    {"LEVEL": 2, "PIN": board.D9, "PREV_TIME": -1},
    {"LEVEL": 3, "PIN": board.D10, "PREV_TIME": -1}
]  # TODO add the other vibrating motors to this list

VIBRATION_TIME = 0.004  # seconds  TODO read from file after calibration
MIN_OFF_TIME = 0.100  # seconds
MAX_OFF_TIME = 1.000  # seconds

EXTEND = 'BSMB_MUSCLE_EXTEND'
FLEX = 'BSMB_MUSCLE_FLEX'
LEVELS = [-4, -3, -2, -1, 0, 1, 2, 3, 4]
MVC = pd.read_csv('emg_files/MVC.csv')  # pick for the correct subject?


def initiate_pin_output(vibrator_list):
    """ Initiate pins and set the direction to output.

    Args:
        vibrator_list (list): list with dictionary with vibrating motor info.
    """
    for vibrator in vibrator_list:
        vibrator["PIN"] = digitalio.DigitalInOut(vibrator["PIN"])
        vibrator["PIN"].direction = digitalio.Direction.OUTPUT


def motor_on(vibrator, on=False):
    """ Turns on or off the vibrating motor by setting the pin value to True
    or False, on or off respectively.

    Args:
        vibrator (dict): Instance from the vibrator_list.
        on (bool, optional): Sets the pin value. Defaults to False (Off).
    """
    vibrator["PIN"].value = on
