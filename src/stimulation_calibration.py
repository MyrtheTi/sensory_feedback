"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-01-16 08:53:01
 * @desc Calibration of vibrators to define comfortable range and
 just noticeable difference.
"""

import math
import time

from activate_vibration_motors import ActivateVibrationMotor

if __name__ == '__main__':
    calibration = {}

    motors = ActivateVibrationMotor()
    levels = []
    # define comfortable range, see Chee et al. 2022
    for vibrator_level in motors.level_list:  # loop through levels
        print('level', vibrator_level)
        motors.set_motor_value(vibrator_level["PIN"], False)  # turn off

        thresholds = [0, 0, 0, 0, 0]
        for repeat in range(5):  # repeat the calibration 5 times
            # pause before continuing
            # TODO look up how to use inputs in circuit python
            input(
                'Press a key if you are ready to start the next calibration\n')

            # report starting to perceive something clear
            # (perceptual threshold) at an intensity of 2/10

            for i in range(1, 10):  # increase duration by 1ms
                on_time = i / 1000  # s on
                print(on_time, 's')
                vibrator_level["VIBRATION_TIME"] = on_time

                start = time.monotonic()
                while time.monotonic() - start < 2:  # activate for 2 s
                    now = time.monotonic()
                    motors.check_time_to_change(vibrator_level, now)

                motors.set_motor_value(vibrator_level["PIN"], False)  # turn off
                user_input = input('press a key if you felt the vibration with an intensity of 2/10')
                if user_input != '':
                    thresholds[repeat] = on_time
                    break
                time.sleep(1)  # pause for 1 second

        levels.append({"LEVEL": vibrator_level["LEVEL"], "thresholds": thresholds})
        print(levels)
        # # take the average
        # calibration[str(vibrator) + '_min'] = math.avg(min)
        # calibration[str(vibrator) + '_max'] = math.avg(max)

        # TODO save these values in a file

# add familiarisation period
# also validate whether participants can differentiate between the vibrators
# see Chee et a. 2022 - Optimally-calibrated non-invasive...
# or as in Tchimino et al. 2022; > 90% is correctly validated here
