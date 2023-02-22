"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-01-23 08:59:19
 * @desc Run this script as code.py on the Seeed board with CircuitPython.
"""

import time

from activate_vibration_motors import ActivateVibrationMotor
from preprocessing import PreprocessEMG
from read_uart import ReadUart

if __name__ == '__main__':
    motors = ActivateVibrationMotor()
    motors.initiate_pin_output()
    motors.configure_levels()

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
            motors.adjust_off_time(level)
        else:
            motors.vib_count = 0
            motors.prev_count = 0
            motors.prev_level = None

        print('level', level)
        for vibrator_level in motors.level_list:

            if vib_emg & (level == vibrator_level["LEVEL"]):  # pin to activate
                motors.check_time_to_change(vibrator_level, now)
            else:  # turn off
                motors.set_motor_value(vibrator_level, False)
