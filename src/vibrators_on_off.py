"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-01-13 11:38:44
 * @desc Turn the vibrators on and off, run with CircuitPython
"""

import time

from utils import VIB_PIN_LIST, initiate_pin_output, motor_on


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

    initiate_pin_output(VIB_PIN_LIST)

    for vibrator in VIB_PIN_LIST:
        motor_on(vibrator)

    for vibrator in VIB_PIN_LIST:  # test motors one by one
        # test sensory threshold; feel 'haptic' short feedback from ~3ms
        for i in range(0, 10):
            on_time = i / 1000  # s on
            print(on_time, 's')
            vibration_frequency(vibrator["PIN"], on_time, 2)

    for vibrator in VIB_PIN_LIST:
        motor_on(vibrator)
