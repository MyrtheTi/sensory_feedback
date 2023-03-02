"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-01-23 08:59:19
 * @desc Run this script as code.py on the Seeed board with CircuitPython.
"""

import gc
import time

from activate_vibration_motors import ActivateVibrationMotor
from preprocessing import PreprocessEMG
from read_uart import ReadUart

if __name__ == '__main__':
    gc.collect()

    vib_emg = False

    read_uart = ReadUart()
    read_uart.initialise_uart()

    user = "me"
    emg_calibration = '2023_02_24'
    feedback_calibration = '2023_03_02'

    motors = ActivateVibrationMotor(user, feedback_calibration)
    motors.get_perception_thresholds()
    motors.set_thresholds()

    process_EMG = PreprocessEMG(user, emg_calibration, extend=1, flex=0)
    gc.collect()

    while True:  # infinite loop
        now = time.monotonic()
        data = read_uart.get_serial_data()
        emg_value = read_uart.extract_emg_data(data)

        normal = process_EMG.normalise_data_MVC(emg_value)
        vib_emg = process_EMG.threshold_reached(normal)

        if vib_emg:
            level = process_EMG.define_dominant_muscle(normal)
            print('level', level)
            motors.adjust_off_time(level)

            index = level + 4
            vibrator_level = motors.level_list[index]
            motors.check_time_to_change(vibrator_level, now)
            pin_on_index = vibrator_level["PIN_INDEX"]
        else:
            print(vib_emg)
            motors.vib_count = 0
            motors.prev_count = 0
            motors.prev_level = None
            pin_on_index = []

        pin_off_index = set(motors.pin_index) - set(pin_on_index)
        pins_off = [motors.pins[pin] for pin in pin_off_index]

        # turn off all others
        motors.set_motor_value(pins_off, False)
        gc.collect()
