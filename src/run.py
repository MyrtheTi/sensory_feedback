"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-01-23 08:59:19
 * @desc Run this script as code.py on the Seeed board with CircuitPython.
"""

import time

from utils import (MAX_OFF_TIME, MIN_OFF_TIME, VIB_PIN_LIST, VIBRATION_TIME,
                   initiate_pin_output, motor_on)

if __name__ == '__main__':
    initiate_pin_output(VIB_PIN_LIST)
    level = 0  # TODO relate to EMG signals
    prev_level = None
    vib_count = 0  # counts the times a motor is turned on sequentially
    prev_count = 0

    while True:  # infinite loop
        now = time.monotonic()

        if level != prev_level:
            # increase frequency if EMG activation changes
            off_time = MIN_OFF_TIME
            vib_count = 0
            prev_count = 0
            prev_level = level
        else:
            if prev_count != vib_count:
                # decrease frequency if the EMG activation is the same
                off_time += 0.100
                prev_count += 1
                if off_time > MAX_OFF_TIME:
                    off_time = MAX_OFF_TIME

        for vibrator in VIB_PIN_LIST:

            if level == vibrator["LEVEL"]:  # correct pin to activate for EMG
                if vibrator["PIN"].value is False:

                    # check whether it is time to turn on
                    if now >= vibrator["PREV_TIME"] + off_time:
                        vibrator["PREV_TIME"] = now
                        motor_on(vibrator, True)
                        vib_count += 1

                if vibrator["PIN"].value is True:

                    # check whether it is time to turn off
                    if now >= vibrator["PREV_TIME"] + VIBRATION_TIME:
                        vibrator["PREV_TIME"] = now
                        motor_on(vibrator, False)
            else:  # turn off
                motor_on(vibrator, False)
