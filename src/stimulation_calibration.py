"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-01-16 08:53:01
 * @desc Calibration of vibrators to define the perceptual threshold for each
 level and save these in a file.
"""

import time

from activate_vibration_motors import ActivateVibrationMotor


def mean(data):
    """ Calculate the mean of a list.

    Args:
        data (list): data to calculate mean from

    Returns:
        float: mean of data
    """
    avg = sum(data) / len(data)
    return avg


def write_file(path, data):
    """ Writes data to a file.

    Args:
        path (string): path and filename of file to write data to
        data (list): list of data to write in file
    """
    with open(path + 'perceptual_thresholds.csv', 'w') as file:
        file.write("%s" % ','.join(str(col) for col in data))


def calibration_loop(motors, vibrator_level):
    """ Increases vibration of vibrator_level with 1 ms at a time with
    intervals of 2 s on, 1 s off. User is asked to confirm continuation to the
    next level and for each step. When the user starts to feel the vibration
    clearly with an intensity of 2/10, i.e. the perceptual threshold is
    reached, input is given by the user and the level is returned.
    Based on Chee et al. 2022, and Tchimino et al. 2022

    Args:
        motors (class): instance from ActivateVibrationMotor
        vibrator_level (dict): level information

    Returns:
        float: vibration_time from the moment the loop is broken
    """
    input('Press enter when you are ready to start the next round\n')
    vibration_time = 0  # s
    on = 0
    while True:
        on += 1
        vibration_time = on / 1000  # increase duration by 1ms
        print(vibration_time, 's')
        vibrator_level["VIBRATION_TIME"] = vibration_time

        motors.vibrate_motor(vibrator_level, 2)

        user_input = input(
            'Enter a key when the vibration had an intensity of 2/10\n')
        if user_input != '':
            perception = vibration_time
            break  # when perceptual threshold is reached
        time.sleep(1)  # pause for 1 second
    return perception


if __name__ == '__main__':
    user = 'me'
    date = '2023_03_02'  # make sure this folder exists
    repeat = 5  # repeat the calibration 5 times

    motors = ActivateVibrationMotor(user, date)
    thresholds = [[] for _ in motors.level_list]

    for _ in range(repeat):
        for index, vibrator_level in enumerate(motors.level_list):
            print('level', vibrator_level)
            motors.set_motor_value(vibrator_level["PIN"], False)  # turn off

            perception = calibration_loop(motors, vibrator_level)
            thresholds[index].append(perception)
        print(thresholds)

    avg_thresholds = [mean(t) for t in thresholds]
    print(avg_thresholds)
    write_file(motors.path, avg_thresholds)
