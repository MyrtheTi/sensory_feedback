"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-01-13 11:38:44
 * @desc Turn the vibrators on and off, run with CircuitPython
"""

import time
import board
import digitalio

D7 = digitalio.DigitalInOut(board.D7)
D7.direction = digitalio.Direction.OUTPUT

D8 = digitalio.DigitalInOut(board.D8)
D8.direction = digitalio.Direction.OUTPUT

D9 = digitalio.DigitalInOut(board.D9)
D9.direction = digitalio.Direction.OUTPUT

D10 = digitalio.DigitalInOut(board.D10)
D10.direction = digitalio.Direction.OUTPUT


def vibrators_off():
    """ Vibrators are turned off when their value is set to False.
    """
    D7.value = False
    D8.value = False
    D9.value = False
    D10.value = False


if __name__ == '__main__':

    vibrators_off()

    for i in range(0, 10):  # test sensory threshold; feel 'haptic' short feedback from ~3ms
        on_time = i / 100  # s on
        print(on_time, 's')
        D8.value = True
        time.sleep(on_time)
        vibrators_off()
        time.sleep(2.0)
        D10.value = True
        time.sleep(on_time)
        vibrators_off()
        time.sleep(2.0)

    vibrators_off()
