"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-01-13 14:13:32
 * @desc Control the strength of the vibrators using PWM
 run with CircuitPython
 When turned on with PWM, the motors create a high pitch sound.
"""

import time

import pwmio

from vibrators_on_off import vibrator_list


def duty_cycle_value(percent):
    """ Calculate the integer from a percentage. """
    return int(percent / 100 * 65535)


def set_duty_cycle(vibrator, intensity, time_on, time_off=0.0):
    """ Turn on the vibration motors for a specified time using PWM.

    Args:
        vibrator (_type_): PWM I/O pin with the direction out.
        intensity (_type_): Sets the duty cycle;
        the percentage of time the motors are turned on.
        time_on (_type_): Number of seconds the motor is turned on.
        time_off (float, optional): _Number of seconds the motor is turned off.
        Defaults to 0.0.
    """
    vibrator.duty_cycle = duty_cycle_value(intensity)
    time.sleep(time_on)
    vibrator.duty_cycle = 0
    time.sleep(time_off)


if __name__ == '__main__':

    for vibrator in vibrator_list:  # set-up pins
        vibrator["PIN"] = pwmio.PWMOut(vibrator["PIN"], duty_cycle=0)

    for vibrator in vibrator_list:  # test motors one by one
        for i in range(3, 10):  # start 'vibration' feeling from 3-5%
            print(i)
            time.sleep(1)

            # test sensory threshold; feel 'haptic' short feedback, but still noise
            for t in range(0, 10):
                on_time = t / 100  # s on
                print(on_time, 's')
                set_duty_cycle(vibrator["PIN"], i, on_time, 2)
