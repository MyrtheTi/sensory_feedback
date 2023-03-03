"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-03-01 13:25:38
 * @desc Script for the familiarisation and validation of the sensory feedback.
 Based on papers from Chee et al. 2022 and Tchimino et al. 2022.
"""

import random
import time

from activate_vibration_motors import ActivateVibrationMotor


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

    Args:
        motors (class): instance from ActivateVibrationMotor
        validation (bool, optional): Defines whether it is a familiarisation or
        validation session. Defaults to False.
        repeat (int, optional): Number of times each level is presented.
        Defaults to 10.
    """
    stimulation_list = motors.level_list * repeat
    print(len(stimulation_list))
    user_answers = []
    stimulated = []

    while stimulation_list:
        if len(stimulation_list) % len(motors.level_list) == 0:
            print(len(stimulation_list) / len(motors.level_list), ' more rounds to go')
        index = random.randrange(len(stimulation_list))
        stimulus = stimulation_list[index]
        stimulation_list.pop(index)

        motors.vibrate_motor(stimulus, 2)
        if validation:
            user = input('Enter level according to the user\n')
            user_answers.append(int(user))
            stimulated.append(stimulus["LEVEL"])
        else:
            print(stimulus)
            input('Enter to continue to next stimulus')
        time.sleep(1)

    print('You are finished!')
    if validation:
        calculate_accuracy(stimulated, user_answers)


def calculate_accuracy(stimulation_list, user_answers):
    """ Calculates the accuracy of the user.

    Args:
        stimulation_list (list): True levels of the stimulus
        user_answers (list): Predicted levels of the stimulus by the user
    """
    # TODO save values somewhere to make a confusion matrix or something similar
    # TODO consider whether level needs to be exact or whether just extend/flex/co-contraction is enough
    correct = sum(1 for x, y in zip(stimulation_list, user_answers) if x == y)
    total = len(stimulation_list)
    accuracy = correct / total
    print(f'The accuracy reached is {accuracy:0.2f}')


if __name__ == '__main__':
    user = 'me'
    date = '2023_03_02'

    motors = ActivateVibrationMotor(user, date)
    motors.get_perception_thresholds()
    motors.set_thresholds()

    validation_loop(motors, validation=False, repeat=2)  # familiarisation
    validation_loop(motors, validation=True, repeat=2)
