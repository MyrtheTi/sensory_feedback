"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-01-23 08:59:19
 * @desc Run this script as code.py on the Seeed board with CircuitPython.
"""

import gc

import supervisor

from activate_vibration_motors import ActivateVibrationMotor
from preprocessing import PreprocessEMG
from read_uart import ReadUart


def online_feedback_loop(
        user, feedback_folder, emg_folder,
        threshold_file='perceptual_threshold.csv', left_leg=True):
    """ Loop to run in code.py on the microprocessor with CircuitPython.
    Online processing of incoming EMG signals and activates the vibration
    motors accordingly.

    Args:
        user (str): user name or number, folder where all user files are saved.
        feedback_folder (str): path to files for thresholds file.
        emg_folder (str): path to files for emg calibration.
        threshold_file (str, optional): file with perceptual thresholds for
        vibration for each level. Defaults to 'perceptual_threshold.csv'.
        left_leg (bool, optional): Whether the motors are placed on the left or
        right leg. Defaults to True.
    """
    gc.collect()
    vib_emg = False

    read_uart = ReadUart()
    read_uart.initialise_uart()

    motors = ActivateVibrationMotor(user, feedback_folder, left_leg)
    motors.set_thresholds(threshold_file)

    process_EMG = PreprocessEMG(user, emg_folder, extend=1, flex=0)
    gc.collect()

    while True:  # infinite loop
        try:
            data = read_uart.get_serial_data()
            if len(data) > 11:  # update level when data is available
                emg_value = read_uart.extract_emg_data(data)
                normal = process_EMG.normalise_data_MVC(emg_value)
                vib_emg = process_EMG.threshold_reached(normal)

                if vib_emg:
                    level = process_EMG.define_dominant_muscle(normal)
                    # print('level', level)
                    index = level + 4
                    vibrator_level = motors.level_list[index]
                    pin_on_index = vibrator_level["PIN_INDEX"]
                else:
                    motors.vib_count = 0
                    motors.prev_count = 0
                    motors.prev_level = None
                    pin_on_index = []

                pin_off_index = set(motors.pin_index) - set(pin_on_index)
                pins_off = [motors.pins[pin] for pin in pin_off_index]

                # turn off all others
                motors.set_motor_value(pins_off, False)

            if vib_emg:
                motors.adjust_off_time(vibrator_level)
                now = supervisor.ticks_ms()
                motors.check_time_to_change(vibrator_level, now)

        except KeyboardInterrupt:  # Turn the motors off nicely
            print('Turning off')
            pins_off = motors.pins
            motors.set_motor_value(pins_off, False)
            gc.collect()
            break


if __name__ == '__main__':
    user = 'me'
    feedback_calibration = '2023_03_28'
    emg_calibration = '2023_02_24'
    threshold_file = 'perceptual_thresholds - Copy.csv'
    left_leg = True

    online_feedback_loop(user, feedback_calibration, emg_calibration,
                         threshold_file, left_leg)
