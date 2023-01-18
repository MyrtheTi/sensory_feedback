"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-01-13 14:13:32
 * @desc Control the strength of the vibrators using PWM
 run with CircuitPython
"""

import time
import board
import pwmio


def duty_cycle_value(percent):
    """ Calculate the integer from a percentage. """
    return int(percent / 100 * 65535)


if __name__ == '__main__':

    D7 = pwmio.PWMOut(board.D7, duty_cycle=0)
    D8 = pwmio.PWMOut(board.D8)
    D9 = pwmio.PWMOut(board.D9)
    D10 = pwmio.PWMOut(board.D10)

    # set the duty cycle; the percentage of time the motors are turned on
    print(D7.frequency)  # find out frequency, default is 500 Hz
    print(D7.variable_frequency)
    for i in range(0, 10):  # start feeling from 3-5%
        print(i)
        D7.duty_cycle = duty_cycle_value(i)
        time.sleep(2)
        D7.duty_cycle = 0
        time.sleep(1)
    D7.duty_cycle = 0  # still makes a noise and doesn't seem to be completely turned off
