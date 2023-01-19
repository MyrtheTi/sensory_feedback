"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-01-13 14:13:32
 * @desc Control the strength of the vibrators using PWM
 run with CircuitPython
 When turned on with PWM, the motors create a high pitch sound.
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

    for i in range(0, 10):  # start 'vibration' feeling from 3-5%
        print(i)
        D8.duty_cycle = duty_cycle_value(i)
        time.sleep(2)
        D8.duty_cycle = 0
        time.sleep(1)
        D9.duty_cycle = duty_cycle_value(i)
        time.sleep(2)
        D9.duty_cycle = 0
        time.sleep(1)
