"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-01-16 08:53:01
 * @desc Calibration of vibrators to define comfortable range and
 just noticeable difference.
"""

import time
import board
import pwmio
import math

from vibrators_PWM import duty_cycle_value


if __name__ == '__main__':
    n_of_vibrators = 4
    output_start = 7
    calibration = {}

    # define comfortable range, see Chee et al. 2022
    for v in range(output_start, output_start + n_of_vibrators):
        output = 'D' + str(v)
        vibrator = pwmio.PWMOut(board.str(output))

        min = [0, 0, 0, 0, 0]
        max = [1, 1, 1, 1, 1]
        # repeat the calibration 5 times
        for i in range(5):
            # pause before continuing
            # TODO look up how to use inputs in circuit python
            input(
                'Press a key if you are ready to start the next calibration\n')

            # 1:
            # report starting to perceive something clear
            # (perceptual threshold) at an intensity of 2/10
            # 2:
            # report whenever the intensity began to be come stronger
            # (remaining below an uncomfortable level) at an intensity of 8/10

            # increase the vibration intensity by 1%, activate 2 s, pause 1 s
            for intensity in range(0, 1, 0.01):

                vibrator.duty_cycle = duty_cycle_value(intensity)
                time.sleep(2)
                vibrator.duty_cycle = 0
                time.sleep(1)
                if input == 'l':  # input for lower threshold, maybe easier in PsychoPy or so?
                    min[i] = intensity
                elif input == 'h':  # input for high threshold
                    max[i] = intensity
                    break

        # take the average
        calibration[str(vibrator) + '_min'] = math.avg(min)
        calibration[str(vibrator) + '_max'] = math.avg(max)

        # TODO save these values in a file

# define just noticeable difference for each vibrating motor;
# TODO maybe do not use stimulation levels?
# but just located stimulation for encoding EMG signals? to keep it more simple?
# start with the minimum value (reference) and minimum + 40 % (test)
# stimulate twice, 1 reference, 1 test, randomise the order
# stimulus 2 s with 1 s pause in between
# participant says which one is higher
# if incorrect, increase the test with 5%
# if correct, the test becomes the new reference
# continue until test would be above maximum
# repeat 5 times
# define the total number of levels

# validate levels for each vibrating motor
# present 2 signals of different or the same levels
# participant says which one is higher or the same
# if > 75% correct, validation is good, otherwise,
# JND calibration needs to be redefined

# also test whether participants can differentiate between the vibrators
# see Chee et a. 2022 - Optimally-calibrated non-invasive...
# or as in Tchimino et al. 2022; > 90% is correctly validated here
