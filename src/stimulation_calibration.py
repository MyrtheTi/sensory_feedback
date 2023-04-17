"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-01-16 08:53:01
 * @desc Calibration of vibrators to define the perceptual threshold for each
 level and save these in a file.
"""

import asyncio
import time

from activate_vibration_motors import ActivateVibrationMotor
from utils import mean, write_file


def calibration_loop(motors):
    """ Increases vibration of vibrator_level with 1 ms at a time with
    intervals of 2 s on, 1 s off. User is asked to confirm continuation to the
    next level and for each step. When the user starts to feel the vibration
    clearly with an intensity of 2/10, i.e. the perceptual threshold is
    reached, input is given by the user and the level is returned.
    Based on Chee et al. 2022, and Tchimino et al. 2022

    Args:
        motors (class): instance from ActivateVibrationMotor

    Returns:
        float: vibration_time from the moment the loop is broken
    """
    input('Press enter when you are ready to start the next round\n')
    vibration_time = 0  # ms
    on = 0
    while True:
        on += 1
        vibration_time = on  # increase duration by 1ms
        print(vibration_time, 'ms')
        motors.vibrator_level["VIBRATION_TIME"] = vibration_time / 1000

        motors.prev_level = None  # so off_time is not adjusted
        asyncio.run(motors.vibrate_motor(2))

        user_input = input(
            'Enter a key when the vibration had an intensity of 2/10\n')
        if user_input != '':
            perception = vibration_time
            break  # when perceptual threshold is reached
        time.sleep(1)  # pause for 1 second
    return perception


if __name__ == '__main__':
    user = 'U747'
    date = '2023_04_17'  # make sure this folder exists
    repeat = 2  # repeat the calibration 5 times
    left_leg = True

    motors = ActivateVibrationMotor(user, date, left_leg)
    thresholds = [[] for _ in motors.level_list]

    for _ in range(repeat):
        for index, vibrator_level in enumerate(motors.level_list):
            print('level', vibrator_level)
            motors.set_motor_value(vibrator_level["PIN"], False)  # turn off
            motors.vibrator_level = vibrator_level

            perception = calibration_loop(motors)
            thresholds[index].append(perception)
        print(thresholds)

    avg_thresholds = [mean(t) for t in thresholds]
    print(avg_thresholds)
    write_file(motors.path, 'perceptual_thresholds.csv', avg_thresholds)
