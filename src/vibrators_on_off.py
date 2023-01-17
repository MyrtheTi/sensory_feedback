"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-01-13 11:38:44
 * @desc Turn the vibrators on and off
 run with CircuitPython
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
    """ Vibrators are turned off when their value is set to True.
    """
    D7.value = True
    D8.value = True
    D9.value = True
    D10.value = True


vibrators_off()

while True:
    D7.value = False
    time.sleep(0.010)
    vibrators_off()
    time.sleep(2.0)

    D8.value = False
    time.sleep(0.010)
    vibrators_off()
    time.sleep(2.0)

    D9.value = False
    time.sleep(0.010)
    vibrators_off()
    time.sleep(2.0)

    D10.value = False
    time.sleep(0.010)
    vibrators_off()
    time.sleep(2.0)
