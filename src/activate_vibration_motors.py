"""
 * @author Myrthe Tilleman
 * @email mtillerman@ossur.com
 * @create date 2023-02-22 11:33:31
 * @desc Class for activating the vibration motors to deliver the sensory
 feedback according to predefined levels.
"""

import time

import board
import digitalio
import supervisor

from utils import read_file


class ActivateVibrationMotor():
    def __init__(self, user, date, left_leg=True):
        self.pins = [board.D0, board.D1, board.D2, board.D3,
                     board.D4, board.D5, board.D8]  # level 3 to -3
        self.level_list = [
            {"LEVEL": -4, "PIN": [4, 5, 6], "PIN_INDEX": [4, 5, 6],
             "PREV_TIME": -1, "VIBRATION_TIME": -1},

            {"LEVEL": -3, "PIN": [6], "PIN_INDEX": [6],
             "PREV_TIME": -1, "VIBRATION_TIME": -1},

            {"LEVEL": -2, "PIN": [5], "PIN_INDEX": [5],
             "PREV_TIME": -1, "VIBRATION_TIME": -1},

            {"LEVEL": -1, "PIN": [4], "PIN_INDEX": [4],
             "PREV_TIME": -1, "VIBRATION_TIME": -1},

            {"LEVEL": 0, "PIN": [3], "PIN_INDEX": [3],
             "PREV_TIME": -1, "VIBRATION_TIME": -1},

            {"LEVEL": 1, "PIN": [2], "PIN_INDEX": [2],
             "PREV_TIME": -1, "VIBRATION_TIME": -1},

            {"LEVEL": 2, "PIN": [1], "PIN_INDEX": [1],
             "PREV_TIME": -1, "VIBRATION_TIME": -1},

            {"LEVEL": 3, "PIN": [0], "PIN_INDEX": [0],
             "PREV_TIME": -1, "VIBRATION_TIME": -1},

            {"LEVEL": 4, "PIN": [0, 1, 2], "PIN_INDEX": [0, 1, 2],
             "PREV_TIME": -1, "VIBRATION_TIME": -1}]

        self.pin_index = list(range(0, len(self.pins)))  # 0 to 7
        self.left_leg = left_leg
        self.min_off_time = 100  # milliseconds
        self.max_off_time = 500  # milliseconds
        self.off_time = self.min_off_time

        self.vib_count = 0  # counts the times a motor is turned on
        self.prev_level = None

        self.path = f'user_files/{user}/{date}/'

        self.initiate_pin_output()
        self.configure_pins()

    def initiate_pin_output(self):
        """ Initiate pins and set the direction to output.
        """
        for i, vibrator in enumerate(self.pins):
            vibrator = digitalio.DigitalInOut(vibrator)
            vibrator.direction = digitalio.Direction.OUTPUT
            self.pins[i] = vibrator

    def configure_pins(self):
        """ Configures the pins for each level. If the right leg is used, the
        pins are reversed, so the cables can always be guided down the leg.
        """
        if not self.left_leg:
            self.pins.reverse()
        for level_conf in self.level_list:
            # level = level_conf["LEVEL"]
            level_conf["PIN"] = [self.pins[i] for i in level_conf["PIN"]]

    def set_thresholds(self, file='perceptual_thresholds.csv'):
        """ Loads file with perceptual thresholds.
        Configures the vibration time for each level.
        """
        self.thresholds = read_file(self.path, file, ['float'])[0]
        for index, level_conf in enumerate(self.level_list):
            level_conf["VIBRATION_TIME"] = self.thresholds[index]

    def set_motor_value(self, pin_list, value=False):
        """ Turns on or off the vibrating motor by setting the pin value to
        True or False, on or off respectively.

        Args:
            pin_list (list): List with digital output pin.
            value (bool, optional): Sets the pin value. Defaults to False.
        """
        for pin in pin_list:
            pin.value = value

    def check_time_to_change(self, level, now):
        """Checks the value of the pins and whether it is time to turn them on
        or off.

        Args:
            level (dict): The level information
            now (timestamp): timestamp of loop
        """
        pin_value = [pin.value for pin in level["PIN"]]

        if all(pin_value) is False:
            # check whether it is time to turn on
            if now >= level["PREV_TIME"] + self.off_time:
                level["PREV_TIME"] = now
                self.set_motor_value(level["PIN"], True)
                self.vib_count += 1

        else:   # pin_value is True
            # check whether it is time to turn off
            if now >= level["PREV_TIME"] + level["VIBRATION_TIME"]:
                level["PREV_TIME"] = now
                self.set_motor_value(level["PIN"], False)

    def adjust_off_time(self, vibrator_level):
        """ Adjusts time the vibrators are turned off. If the level is the
        same for 2 seconds, the motors vibrate with a longer interval,
        at max_off_time. If the level changes, the off_time resets.

        Args:
            vibrator_level (dict): Information of the current level.
        """
        level = vibrator_level["LEVEL"]
        if level != self.prev_level:
            # resets frequency if EMG activation changes
            self.off_time = self.min_off_time
            self.vib_count = 0
            self.prev_level = level
        else:
            vibration_time = vibrator_level["VIBRATION_TIME"]
            # more than 2 seconds the same level
            if (vibration_time + self.min_off_time) * self.vib_count > 2000:
                # decrease frequency if the EMG activation is the same
                self.off_time = self.max_off_time

    def vibrate_motor(self, vibrator_level, duration=2):
        """ Activate motor specified by vibrator_level for duration.

        Args:
            vibrator_level (dict): Level information
            duration (int, optional): Time (in seconds) the motor should
            vibrate on and off. Defaults to 2.
        """
        start = supervisor.ticks_ms()
        while supervisor.ticks_ms() - start < (duration * 1000):
            now = supervisor.ticks_ms()
            self.check_time_to_change(vibrator_level, now)
            self.adjust_off_time(vibrator_level)
        self.set_motor_value(vibrator_level["PIN"], False)  # turn off


if __name__ == "__main__":
    user = 'me'
    date = '2023_03_28'  # make sure this folder exists
    left_leg = True
    motors = ActivateVibrationMotor(user, date, left_leg)
    motors.set_thresholds('perceptual_thresholds - Copy.csv')

    for vibrator_level in motors.level_list:  # loop through levels
        print('level', vibrator_level)
        motors.vibrate_motor(vibrator_level, 2)
        time.sleep(1)
    print(motors.level_list)
