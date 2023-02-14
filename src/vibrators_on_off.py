"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-01-13 11:38:44
 * @desc Turn the vibrators on and off, run with CircuitPython
"""

import time

from utils import VIB_PIN_LIST, initiate_pin_output, motor_on, LEVEL_LIST


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
    off_time = 0.1
    on_time = 0.004  # s on

    for vibrator in VIB_PIN_LIST:
        motor_on(vibrator)

    for vibrator_level in LEVEL_LIST:  # loop through levels
        pins = vibrator_level["PIN"]
        print('level', vibrator_level["LEVEL"])

        start = time.monotonic()
        while time.monotonic() - start < 5:  # vibrate each level for 5 seconds
            now = time.monotonic()
            for i, pin in enumerate(pins):
                if VIB_PIN_LIST[pin]["PIN"].value is False:

                    # check whether it is time to turn on
                    if now >= vibrator_level["PREV_TIME"][i] + off_time:
                        vibrator_level["PREV_TIME"][i] = now
                        motor_on(VIB_PIN_LIST[pin], True)

                if VIB_PIN_LIST[pin]["PIN"].value is True:

                    # check whether it is time to turn off
                    if now >= vibrator_level["PREV_TIME"][i] + on_time:
                        vibrator_level["PREV_TIME"][i] = now
                        motor_on(VIB_PIN_LIST[pin], False)

        for vibrator in VIB_PIN_LIST:  # turn all motors off
            motor_on(vibrator)
