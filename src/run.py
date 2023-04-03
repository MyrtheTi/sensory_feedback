"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-01-23 08:59:19
 * @desc Run this script as code.py on the Seeed board with CircuitPython.
"""

import asyncio
import gc

import supervisor

from activate_vibration_motors import ActivateVibrationMotor
from preprocessing import PreprocessEMG
from read_uart import ReadUart


async def check_serial_input(read_uart, process_EMG, motors):
    """ Task 1: Check for emg signals and process them when it is available.

    Args:
        read_uart (Class): ReadUart instance.
        process_EMG (Class): PreprocessEMG instance.
        motors (Class): ActivateVibrationMotor instance.
    """
    while True:
        data = read_uart.get_serial_data()
        if len(data) > 11:  # update level when data is available
            emg_value = read_uart.extract_emg_data(data)
            normal = process_EMG.normalise_data_MVC(emg_value)
            motors.vib_emg = process_EMG.threshold_reached(normal)

            if motors.vib_emg:
                level = process_EMG.define_dominant_muscle(normal)
                # print('level', level)
                index = level + 4
                motors.vibrator_level = motors.level_list[index]
                motors.pin_on_index = motors.vibrator_level["PIN_INDEX"]
            else:
                motors.vib_count = 0
                motors.prev_count = 0
                motors.prev_level = None
                motors.pin_on_index = []
        await asyncio.sleep(0)


async def activate_motors(motors):
    """ Task 2: Activate and deactivate the vibration motors.

    Args:
        motors (Class): ActivateVibrationMotor instance.
    """
    while True:
        pin_off_index = set(motors.pin_index) - set(motors.pin_on_index)
        pins_off = [motors.pins[pin] for pin in pin_off_index]

        # turn off all others
        motors.set_motor_value(pins_off, False)

        if motors.vib_emg:
            motors.adjust_off_time(motors.vibrator_level)
            now = supervisor.ticks_ms()
            motors.check_time_to_change(motors.vibrator_level, now)
        await asyncio.sleep(0)


async def online_feedback_loop(
        user, feedback_folder, emg_folder,
        threshold_file='perceptual_threshold.csv', left_leg=True):
    """ Loop to run in code.py on the microprocessor with CircuitPython.
    Online processing of incoming EMG signals and activates the vibration
    motors accordingly. Creates two asyncio tasks and runs these alternately.

    Args:
        user (str): user name or number, folder where all user files are saved.
        feedback_folder (str): path to files for thresholds file.
        emg_folder (str): path to files for emg calibration.
        threshold_file (str, optional): file with perceptual thresholds for
        vibration for each level. Defaults to 'perceptual_threshold.csv'.
        left_leg (bool, optional): Whether the motors are placed on the left or
        right leg. Defaults to True.
    """
    read_uart = ReadUart()

    motors = ActivateVibrationMotor(user, feedback_folder, left_leg)
    motors.set_thresholds(threshold_file)

    process_EMG = PreprocessEMG(user, emg_folder, extend=1, flex=0)

    emg_collection_task = asyncio.create_task(
        check_serial_input(read_uart, process_EMG, motors))

    vibration_task = asyncio.create_task(activate_motors(motors))
    gc.collect()

    await asyncio.gather(emg_collection_task, vibration_task)


if __name__ == '__main__':
    user = 'me'
    feedback_calibration = '2023_03_28'
    emg_calibration = '2023_02_24'
    threshold_file = 'perceptual_thresholds - Copy.csv'
    left_leg = True

    asyncio.run(online_feedback_loop(
        user, feedback_calibration, emg_calibration, threshold_file, left_leg))
