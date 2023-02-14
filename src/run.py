"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-01-23 08:59:19
 * @desc Run this script as code.py on the Seeed board with CircuitPython.
"""

import time

from preprocessing import PreprocessEMG
from read_uart import ReadUart
from utils import (LEVEL_LIST, MAX_OFF_TIME, MIN_OFF_TIME, VIB_PIN_LIST,
                   VIBRATION_TIME, initiate_pin_output, motor_on)

if __name__ == '__main__':
    initiate_pin_output(VIB_PIN_LIST)
    level = 0  # TODO relate to EMG signals
    prev_level = None
    vib_count = 0  # counts the times a motor is turned on sequentially
    prev_count = 0
    vib_emg = False

    read_uart = ReadUart()
    read_uart.initialise_uart()

    process_EMG = PreprocessEMG('MVC.csv', extend=1, flex=0)
    process_EMG.get_MVC()

    while True:  # infinite loop
        now = time.monotonic()
        data = read_uart.get_serial_data()
        emg_value = read_uart.extract_emg_data(data)

        normal = process_EMG.normalise_data_MVC(emg_value)
        vib_emg = process_EMG.threshold_reached(normal)

        if vib_emg:
            level = process_EMG.define_dominant_muscle(normal)
            if level != prev_level:
                # increase frequency if EMG activation changes
                off_time = MIN_OFF_TIME
                vib_count = 0
                prev_count = 0
                prev_level = level
            else:
                if prev_count != vib_count:
                    # decrease frequency if the EMG activation is the same
                    off_time += 0.100
                    prev_count += 1
                    if off_time > MAX_OFF_TIME:
                        off_time = MAX_OFF_TIME
        else:
            vib_count = 0
            prev_count = 0
            prev_level = None

        print('level', level)
        for vibrator_level in LEVEL_LIST:

            pins = vibrator_level["PIN"]
            if vib_emg & (level == vibrator_level["LEVEL"]):  # pin to activate
                for pin in pins:
                    if VIB_PIN_LIST[pin]["PIN"].value is False:

                        # check whether it is time to turn on
                        if now >= vibrator_level["PREV_TIME"] + off_time:
                            vibrator_level["PREV_TIME"] = now
                            motor_on(VIB_PIN_LIST[pin], True)
                            vib_count += 1

                    if VIB_PIN_LIST[pin]["PIN"].value is True:

                        # check whether it is time to turn off
                        if now >= vibrator_level["PREV_TIME"] + VIBRATION_TIME:
                            vibrator_level["PREV_TIME"] = now
                            motor_on(VIB_PIN_LIST[pin], False)
            else:  # turn off
                for pin in pins:
                    motor_on(VIB_PIN_LIST[pin], False)
