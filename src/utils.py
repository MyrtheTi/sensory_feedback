"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-01-23 08:59:49
 * @desc Script with utility functions and predefined parameters.
"""

try:
    import board
    import digitalio

    VIB_PIN_LIST = [
        {"PIN": board.D0},
        {"PIN": board.D1},
        {"PIN": board.D2},
        {"PIN": board.D3},
        {"PIN": board.D4},
        {"PIN": board.D5},
        {"PIN": board.D6}
    ]
except ModuleNotFoundError:
    print('This code is not run with CircuitPython')
    pass

LEVEL_LIST = [
    {"LEVEL": -4, "PIN": [4, 5, 6], "PREV_TIME": -1, "VIBRATION_TIME": -1},
    {"LEVEL": -3, "PIN": [6], "PREV_TIME": -1, "VIBRATION_TIME": -1},
    {"LEVEL": -2, "PIN": [5], "PREV_TIME": -1, "VIBRATION_TIME": -1},
    {"LEVEL": -1, "PIN": [4], "PREV_TIME": -1, "VIBRATION_TIME": -1},
    {"LEVEL": 0, "PIN": [3], "PREV_TIME": -1, "VIBRATION_TIME": -1},
    {"LEVEL": 1, "PIN": [2], "PREV_TIME": -1, "VIBRATION_TIME": -1},
    {"LEVEL": 2, "PIN": [1], "PREV_TIME": -1, "VIBRATION_TIME": -1},
    {"LEVEL": 3, "PIN": [0], "PREV_TIME": -1, "VIBRATION_TIME": -1},
    {"LEVEL": 4, "PIN": [2, 1, 0], "PREV_TIME": -1, "VIBRATION_TIME": -1}
    ]  # when cables down on left leg

VIBRATION_TIME = 0.004  # seconds  TODO read from file after calibration
MIN_OFF_TIME = 0.100  # seconds
MAX_OFF_TIME = 1.000  # seconds

LEVELS = [-4, -3, -2, -1, 0, 1, 2, 3, 4]


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


def get_MVC(file_name):
    """Opens file with maximum voluntary contraction (mvc) values of the user.
    Reads the file and returns the mvc values as a list of integers in the
    same order as the uart data.

    Args:
        file_name (_type_): csv or text file with mvc data, first line is headers

    Returns:
        list: integers of mvc in the order [flex, extend]
    """
    with open(file_name, 'r') as file:
        lines = file.read().splitlines()

    names = lines[0].split(',')

    extend = 1  # order of uart data
    flex = 0

    emg = lines[1].split(',')

    emg_0 = int(float(emg[0]))  # convert to int
    emg_1 = int(float(emg[1]))

    if 'EXTEND' in names[0]:  # if first column is extend emg
        emg_extend = emg_0
        emg_flex = emg_1
    else:
        emg_extend = emg_1
        emg_flex = emg_0

    mvc = {names[0]: emg_0, names[1]: emg_1,
           flex: emg_flex, extend: emg_extend}
    return mvc
