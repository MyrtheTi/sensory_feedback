"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-01-13 11:38:44
 * @desc Turn the vibrators on and off, run with CircuitPython
"""

import time

import board
import digitalio


vibrator_list = [
    {"PIN": board.D7},
    {"PIN": board.D8},
    {"PIN": board.D9},
    {"PIN": board.D10}
]


def vibrators_off(vibrator_list):
    """ Vibrators are turned off when their value is set to False.
    Only works after the pins have been set to 'DigitalInOut'.
    """
    for vibrator in vibrator_list:
        vibrator["PIN"].value = False


def vibration_frequency(vibrator, time_on, time_off=0.0):
    """Turn the vibration motors on and off for a specified amount of time.

    Args:
        vibrator (_type_): Digital I/O pin with the direction OUTPUT.
        time_on (_type_): Number of seconds the motor is turned on.
        time_off (float, optional): Number of seconds the motor is turned off.
        Defaults to 0.0.
    """
    vibrator.value = True
    time.sleep(time_on)
    vibrator.value = False
    time.sleep(time_off)


if __name__ == '__main__':

    for vibrator in vibrator_list:  # set-up pins
        vibrator["PIN"] = digitalio.DigitalInOut(vibrator["PIN"])
        vibrator["PIN"].direction = digitalio.Direction.OUTPUT

    vibrators_off(vibrator_list)
    for vibrator in vibrator_list:  # test motors one by one
        # test sensory threshold; feel 'haptic' short feedback from ~3ms
        for i in range(0, 10):
            on_time = i / 1000  # s on
            print(on_time, 's')
            vibration_frequency(vibrator["PIN"], on_time, 2)

    vibrators_off(vibrator_list)
