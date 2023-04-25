"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-03-01 13:25:38
 * @desc Script for the familiarisation and validation of the sensory feedback.
 Based on papers from Chee et al. 2022 and Tchimino et al. 2022.
"""

import asyncio
import random
import time

from activate_vibration_motors import ActivateVibrationMotor
from utils import write_file


def validation_loop(motors, validation=False, repeat=10):
    """ Loop for familiarisation and validation session. The participant is in
    a static position. Each level is activated a repeat number of times and is
    presented in a random order for 2 s followed by 1 second of rest.
    For each activation, the participant is asked to report which level was
    activated. When incorrect, the researcher provides the correct answer
    during the familiarisation session.
    During the validation, the user is asked to enter the correct level. No
    correct answer is provided. In the end, the accuracy is printed. When 90 %
    or more of the levels were identified correctly, the validation was deemed
    successful.

    Try to save the true and predicted labels in csv files if write access is
    given.
    Args:
        motors (class): instance from ActivateVibrationMotor
        validation (bool, optional): Defines whether it is a familiarisation or
        validation session. Defaults to False.
        repeat (int, optional): Number of times each level is presented.
        Defaults to 10.
    """
    stimulation_list = motors.level_list * repeat
    user_answers = []
    stimulated = []

    while stimulation_list:
        if len(stimulation_list) % len(motors.level_list) == 0:
            input(f'{int(len(stimulation_list) / len(motors.level_list))} '
                  'more round(s) to go')
        index = random.randrange(len(stimulation_list))
        motors.vibrator_level = stimulation_list[index]
        motors.off_time = motors.min_off_time  # off_time shouldn't be adjusted
        stimulation_list.pop(index)

        asyncio.run(motors.vibrate_motor(2))
        if validation:
            user = input('Enter level according to the user\n')
            user_answers.append(int(user))
            stimulated.append(motors.vibrator_level["LEVEL"])
        else:
            print(motors.vibrator_level["LEVEL"])
            input('Enter to continue to next stimulus')
        time.sleep(1)

    print('You are finished!\n')
    if validation:
        calculate_accuracy(stimulated, user_answers)
        try:
            write_file(motors.path, 'true_labels.csv', stimulated)
            write_file(motors.path, 'predicted_labels.csv', user_answers)
        except OSError:
            print('Could not save the data.')
            print('True labels:', stimulated)
            print('Predicted labels:', user_answers)


def calculate_accuracy(stimulation_list, user_answers):
    """ Calculates the accuracy of the user. Using a strictly (only the exact
    level is regarded as correct) and loosely (direction needs to be correct,
    e.g. flex, extend, co-contraction).

    Args:
        stimulation_list (list): True levels of the stimulus
        user_answers (list): Predicted levels of the stimulus by the user
    """
    correct_strict = sum(1 for x, y in zip(stimulation_list, user_answers) if (
        x == y))
    correct_loose = sum(1 for x, y in zip(stimulation_list, user_answers) if (
        (x == y) or (x < 0 and y < 0) or (x > 0 and y > 0)))
    total = len(stimulation_list)
    accuracy_strict = correct_strict / total
    accuracy_loose = correct_loose / total
    print(f'The strict accuracy reached is {accuracy_strict:0.2f} and \
          the loose accuracy reached is {accuracy_loose:0.2f}.')


if __name__ == '__main__':
    user = 'U401'
    date = '2023_04_25'
    left_leg = False

    motors = ActivateVibrationMotor(user, date, left_leg)
    motors.set_thresholds()
    input('Press enter to start the familiarisation and validation')
    validation_loop(motors, validation=False, repeat=4)  # familiarisation
    validation_loop(motors, validation=True, repeat=4)
